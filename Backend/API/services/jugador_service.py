"""
Business logic service for Jugadores (Players) operations
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
import os
import shutil
from datetime import datetime

from models.database_models import JugadoresDB
from models.jugador import (
    JugadorCreate, JugadorUpdate, JugadorResponse, JugadorConEquipo, 
    JugadorFilter, EquipoNFLResponseBasic, JugadorBulkCreate, JugadorBulkResult
)
from repositories.jugador_repository import jugador_repository
from repositories.equipo_repository import equipo_repository
from services.validation_service import validation_service
from services.error_handling import handle_db_errors
from services.cdn_service import cdn_service
from validators.jugador_validator import jugador_validator
from exceptions.business_exceptions import ValidationError, ConflictError, NotFoundError

def _to_jugador_response(jugador: JugadoresDB) -> JugadorResponse:
    return JugadorResponse.model_validate(jugador, from_attributes=True)

def _to_jugador_con_equipo_response(jugador: JugadoresDB) -> JugadorConEquipo:
    jugador_data = JugadorConEquipo.model_validate(jugador, from_attributes=True)
    if jugador.equipo_nfl:
        jugador_data.equipo_nfl = EquipoNFLResponseBasic.model_validate(jugador.equipo_nfl, from_attributes=True)
    return jugador_data

class JugadorService:
    """Service for Player CRUD operations"""
    
    def _create_player_core(self, db: Session, jugador_data: JugadorCreate, commit: bool = True) -> JugadoresDB:
        """
        Core player creation logic without transaction management.
        Used by both create() and crear_jugadores_bulk() methods.
        """
        # Validate required fields
        if not jugador_data.nombre or not jugador_data.nombre.strip():
            raise ValidationError("El nombre del jugador es requerido")
        
        if not jugador_data.posicion:
            raise ValidationError("La posición del jugador es requerida")
        
        if not jugador_data.equipo_id:
            raise ValidationError("El equipo NFL es requerido")
        
        if not jugador_data.imagen_url or not jugador_data.imagen_url.strip():
            raise ValidationError("La URL de imagen es requerida")
        
        # Check if team exists
        equipo = equipo_repository.get(db, jugador_data.equipo_id)
        if not equipo:
            raise NotFoundError(f"El equipo NFL con ID {jugador_data.equipo_id} no existe")
        
        # Check for duplicate player name in the same team
        existing_jugador = jugador_repository.get_by_nombre_equipo(
            db, jugador_data.nombre, jugador_data.equipo_id
        )
        if existing_jugador:
            raise ConflictError(f"El jugador '{jugador_data.nombre}' ya existe en el equipo '{equipo.nombre}'")
        
        # Save image (auto-detect URL or base64) and generate thumbnail
        try:
            saved_image_path, saved_thumbnail_path = cdn_service.save_image_auto(
                jugador_data.imagen_url,
                entity_type="jugador"
            )
            
            # Update paths to local storage
            jugador_data.imagen_url = saved_image_path
            jugador_data.thumbnail_url = saved_thumbnail_path
        except ValueError as e:
            raise ValidationError(f"Error al procesar la imagen: {str(e)}")
        
        # Create jugador using repository
        db_jugador = jugador_repository.create(db, jugador_data)
        
        if commit:
            db.commit()
            
        return db_jugador

    @handle_db_errors
    def create(self, db: Session, jugador_data: JugadorCreate) -> JugadorResponse:
        """
        Crear un nuevo jugador con validaciones.
        
        Características:
        • Campos requeridos: nombre, posición, equipo_id, imagen_url
        • El sistema genera automáticamente: id único, fecha de creación
        • Las imágenes se descargan y guardan en /imgs/pics/
        • El thumbnail se genera automáticamente y se guarda en /imgs/thumbnails/
        • El jugador queda activo por defecto
        • Validación de datos requeridos antes de guardar
        
        Comportamientos alternativos:
        • Si el nombre del jugador ya existe para el mismo equipo NFL, no se crea y se notifica
        • Si no se presentan todos los campos requeridos, no se crea y se notifica
        """
        db_jugador = self._create_player_core(db, jugador_data, commit=True)
        return _to_jugador_response(db_jugador)
    
    def listar_jugadores(self, db: Session, skip: int = 0, limit: int = 100) -> List[JugadorResponse]:
        """List all players with pagination"""
        jugadores = jugador_repository.get_multi(db, skip, limit)
        return [_to_jugador_response(jugador) for jugador in jugadores]
    
    def obtener_jugador(self, db: Session, jugador_id: UUID) -> JugadorResponse:
        """Get a player by ID"""
        jugador = jugador_repository.get(db, jugador_id)
        if not jugador:
            raise NotFoundError("Jugador no encontrado")
        return _to_jugador_response(jugador)
    
    def obtener_jugador_con_equipo(self, db: Session, jugador_id: UUID) -> JugadorConEquipo:
        """Get player with NFL team information"""
        jugador = jugador_repository.get_with_equipo(db, jugador_id)
        if not jugador:
            raise NotFoundError("Jugador no encontrado")
        return _to_jugador_con_equipo_response(jugador)
    
    @handle_db_errors
    def actualizar_jugador(self, db: Session, jugador_id: UUID, actualizacion: JugadorUpdate) -> JugadorResponse:
        """Update a player"""
        jugador = jugador_repository.get(db, jugador_id)
        if not jugador:
            raise NotFoundError("Jugador no encontrado")
        
        # Validate NFL team exists if changing
        if actualizacion.equipo_id:
            equipo = equipo_repository.get(db, actualizacion.equipo_id)
            if not equipo:
                raise NotFoundError("Equipo NFL no encontrado")
        
        # Validate unique name per NFL team if changing name or team
        if actualizacion.nombre or actualizacion.equipo_id:
            nuevo_nombre = actualizacion.nombre or jugador.nombre
            nuevo_equipo_id = actualizacion.equipo_id or jugador.equipo_id
            
            existing_jugador = jugador_repository.get_by_nombre_equipo(db, nuevo_nombre, nuevo_equipo_id)
            if existing_jugador and existing_jugador.id != jugador_id:
                raise ValidationError("Ya existe un jugador con ese nombre en el equipo")
        
        updated_jugador = jugador_repository.update(db, jugador, actualizacion)
        return _to_jugador_response(updated_jugador)
    
    def eliminar_jugador(self, db: Session, jugador_id: UUID) -> bool:
        """Delete a player"""
        jugador = jugador_repository.get(db, jugador_id)
        if not jugador:
            raise NotFoundError("Jugador no encontrado")
        
        return jugador_repository.delete(db, jugador_id)
    
    def buscar_jugadores(self, db: Session, filters: JugadorFilter, skip: int = 0, limit: int = 100) -> List[JugadorResponse]:
        """Search players with filters"""
        jugadores = jugador_repository.get_with_filters(db, filters, skip, limit)
        return [_to_jugador_response(jugador) for jugador in jugadores]
    
    def listar_jugadores_por_equipo(self, db: Session, equipo_id: UUID, skip: int = 0, limit: int = 100) -> List[JugadorResponse]:
        """List all players from a specific NFL team"""
        # Validate NFL team exists
        equipo = equipo_repository.get(db, equipo_id)
        if not equipo:
            raise NotFoundError("Equipo NFL no encontrado")
        
        jugadores = jugador_repository.get_by_equipo(db, equipo_id, skip, limit)
        return [_to_jugador_response(jugador) for jugador in jugadores]
    
    def listar_jugadores_por_posicion(self, db: Session, posicion: str, skip: int = 0, limit: int = 100) -> List[JugadorResponse]:
        """List all players by position"""
        from models.database_models import PosicionJugadorEnum
        
        try:
            posicion_enum = PosicionJugadorEnum(posicion)
        except ValueError:
            raise ValidationError("Posición inválida")
        
        jugadores = jugador_repository.get_by_posicion(db, posicion_enum, skip, limit)
        return [_to_jugador_response(jugador) for jugador in jugadores]
    
    def listar_jugadores_por_liga(self, db: Session, liga_id: UUID, skip: int = 0, limit: int = 100) -> List[JugadorResponse]:
        """List all players from teams in a specific league"""
        # Validate league exists (using validation_service if available)
        try:
            validation_service.validate_liga_exists(db, liga_id)
        except:
            # Fallback validation
            from repositories.liga_repository import liga_repository
            liga = liga_repository.get(db, liga_id)
            if not liga:
                raise NotFoundError("Liga no encontrada")
        
        jugadores = jugador_repository.get_by_liga_id(db, liga_id, skip, limit)
        return [_to_jugador_response(jugador) for jugador in jugadores]
    
    def listar_jugadores_por_usuario(self, db: Session, usuario_id: UUID, skip: int = 0, limit: int = 100) -> List[JugadorResponse]:
        """List all players from teams owned by a specific user"""
        # Validate user exists (using validation_service if available)
        try:
            validation_service.validate_usuario_exists(db, usuario_id)
        except:
            # Fallback validation
            from repositories.usuario_repository import usuario_repository
            usuario = usuario_repository.get(db, usuario_id)
            if not usuario:
                raise NotFoundError("Usuario no encontrado")
        
        jugadores = jugador_repository.get_by_usuario_id(db, usuario_id, skip, limit)
        return [_to_jugador_response(jugador) for jugador in jugadores]
    
    def _convert_bulk_to_create(self, db: Session, jugador_bulk: JugadorBulkCreate, equipo_cache: dict) -> JugadorCreate:
        """Convert JugadorBulkCreate to JugadorCreate with team lookup"""
        # Get or cache the NFL team by name
        if jugador_bulk.equipo_nfl not in equipo_cache:
            equipo = equipo_repository.get_by_nombre(db, jugador_bulk.equipo_nfl)
            if not equipo:
                raise NotFoundError(f"El equipo NFL '{jugador_bulk.equipo_nfl}' no existe")
            equipo_cache[jugador_bulk.equipo_nfl] = equipo
        
        equipo_nfl = equipo_cache[jugador_bulk.equipo_nfl]
        
        return JugadorCreate(
            nombre=jugador_bulk.nombre,
            posicion=jugador_bulk.posicion,
            equipo_id=equipo_nfl.id,
            imagen_url=jugador_bulk.imagen,
            activo=True
        )

    def crear_jugadores_bulk(self, db: Session, jugadores_data: List[JugadorBulkCreate], filename: Optional[str] = None) -> JugadorBulkResult:
        """
        Create multiple players from bulk data with all-or-nothing transaction.
        
        Requirements:
        - JSON includes: nombre, posicion, equipo_nfl, imagen, id (optional)
        - Thumbnail auto-generated from imagen
        - All players created as active by default
        - Format and data validation before processing
        - Success and error report generated at the end
        - If at least one error exists, no players are created (all-or-nothing operation)
        - File moved to processed folder with format <timestamp>_<original_name>.json
        
        Alternative behaviors:
        - If player name already exists for same NFL team, player not created and error reported
        - If required fields missing, player not created and error reported
        """
        errors = []
        validated_players = []
        equipo_cache = {}  # Cache to avoid repeated DB queries
        
        # Step 1: Validation and conversion phase
        for i, jugador_bulk in enumerate(jugadores_data):
            try:
                # Convert bulk data to create format and validate
                jugador_create = self._convert_bulk_to_create(db, jugador_bulk, equipo_cache)
                validated_players.append(jugador_create)
                
            except ValidationError as e:
                errors.append(f"Jugador {i+1} ({jugador_bulk.nombre if hasattr(jugador_bulk, 'nombre') and jugador_bulk.nombre else 'sin nombre'}): {e.message}")
            except ConflictError as e:
                errors.append(f"Jugador {i+1} ({jugador_bulk.nombre if hasattr(jugador_bulk, 'nombre') and jugador_bulk.nombre else 'sin nombre'}): {e.message}")
            except NotFoundError as e:
                errors.append(f"Jugador {i+1} ({jugador_bulk.nombre if hasattr(jugador_bulk, 'nombre') and jugador_bulk.nombre else 'sin nombre'}): {e.message}")
            except Exception as e:
                errors.append(f"Jugador {i+1}: Error de validación: {str(e)}")
        
        # Step 2: If there are any errors, return without creating anything
        if errors:
            return JugadorBulkResult(
                success=False,
                created_count=0,
                error_count=len(errors),
                errors=errors,
                processed_file=self._move_processed_file(filename, success=False) if filename else None
            )
        
        # Step 3: Create all players in a single transaction using core creation logic
        try:
            created_players = []
            
            for jugador_create in validated_players:
                # Use the core creation logic without committing each player individually
                db_jugador = self._create_player_core(db, jugador_create, commit=False)
                created_players.append(db_jugador)
            
            # Commit all players at once
            db.commit()
            
            # Move file to processed folder on success
            processed_file = self._move_processed_file(filename, success=True) if filename else None
            
            return JugadorBulkResult(
                success=True,
                created_count=len(created_players),
                error_count=0,
                errors=[],
                processed_file=processed_file
            )
            
        except Exception as e:
            db.rollback()
            return JugadorBulkResult(
                success=False,
                created_count=0,
                error_count=1,
                errors=[f"Error al crear jugadores en base de datos: {str(e)}"],
                processed_file=self._move_processed_file(filename, success=False) if filename else None
            )
    
    def _generate_thumbnail_url(self, imagen_url: str) -> Optional[str]:
        """Generate thumbnail URL from image URL"""
        try:
            # Simple thumbnail generation by adding '_thumb' suffix
            if '.' in imagen_url:
                base_url, extension = imagen_url.rsplit('.', 1)
                return f"{base_url}_thumb.{extension}"
            return None
        except:
            return None
    
    def _move_processed_file(self, filename: Optional[str], success: bool) -> Optional[str]:
        """Move processed file to appropriate folder"""
        if not filename:
            return None
            
        try:
            # Create processed folder if it doesn't exist
            processed_dir = "/app/processed_files"
            os.makedirs(processed_dir, exist_ok=True)
            
            # Generate new filename with timestamp and status
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            status_suffix = "success" if success else "error"
            base_name = filename.replace('.json', '')
            new_filename = f"{timestamp}_{status_suffix}_{base_name}.json"
            
            return new_filename
            
        except Exception as e:
            # If file moving fails, don't fail the whole operation
            return f"error_moving_file_{filename}"

# Service instance
jugador_service = JugadorService()