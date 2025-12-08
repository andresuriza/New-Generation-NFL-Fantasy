"""
Business logic service for Jugadores (Players) operations
"""
from typing import List, Optional
from uuid import UUID
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
    
    def _create_player_core(self,  jugador_data: JugadorCreate) -> JugadoresDB:
        """
        Core player creation logic without transaction management.
        Used by both create() and crear_jugadores_bulk() methods.
        """
        # Validate all requirements for creating a player
        jugador_validator.validate_for_create(
            jugador_data.nombre,
            jugador_data.posicion,
            jugador_data.equipo_id,
            jugador_data.imagen_url
        )
        
        # Check if team exists
        equipo = equipo_repository.get(jugador_data.equipo_id)
        if not equipo:
            raise NotFoundError(f"El equipo NFL con ID {jugador_data.equipo_id} no existe")
        
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
        
        # Create jugador using repository (commit is handled automatically)
        db_jugador = jugador_repository.create(jugador_data)
        
        return db_jugador

    @handle_db_errors
    def create(self,  jugador_data: JugadorCreate) -> JugadorResponse:
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
        db_jugador = self._create_player_core(jugador_data)
        return _to_jugador_response(db_jugador)
    
    def listar_jugadores(self, skip: int = 0, limit: int = 100) -> List[JugadorResponse]:
        """List all players with pagination"""
        jugadores = jugador_repository.get_multi(skip, limit)
        return [_to_jugador_response(jugador) for jugador in jugadores]
    
    def obtener_jugador(self,jugador_id: UUID) -> JugadorResponse:
        """Get a player by ID"""
        jugador = jugador_repository.get(jugador_id)
        if not jugador:
            raise NotFoundError("Jugador no encontrado")
        return _to_jugador_response(jugador)
    
    def obtener_jugador_con_equipo(self, jugador_id: UUID) -> JugadorConEquipo:
        """Get player with NFL team information"""
        jugador = jugador_repository.get_with_equipo(jugador_id)
        if not jugador:
            raise NotFoundError("Jugador no encontrado")
        return _to_jugador_con_equipo_response(jugador)
    
    @handle_db_errors
    def actualizar_jugador(self, jugador_id: UUID, actualizacion: JugadorUpdate) -> JugadorResponse:
        """Update a player"""
        # Validate all requirements for updating
        jugador = jugador_validator.validate_for_update(
            jugador_id,
            actualizacion.nombre,
            actualizacion.equipo_id
        )
        
        # Validate NFL team exists if changing
        if actualizacion.equipo_id:
            equipo = equipo_repository.get(actualizacion.equipo_id)
            if not equipo:
                raise NotFoundError("Equipo NFL no encontrado")
        
        updated_jugador = jugador_repository.update(jugador, actualizacion)
        return _to_jugador_response(updated_jugador)
    
    def eliminar_jugador(self, jugador_id: UUID) -> bool:
        """Delete a player"""
        jugador = jugador_repository.get(jugador_id)
        if not jugador:
            raise NotFoundError("Jugador no encontrado")
        
        return jugador_repository.delete(jugador_id)
    
    def buscar_jugadores(self, filters: JugadorFilter, skip: int = 0, limit: int = 100) -> List[JugadorResponse]:
        """Search players with filters"""
        jugadores = jugador_repository.get_with_filters(filters, skip, limit)
        return [_to_jugador_response(jugador) for jugador in jugadores]
    
    def listar_jugadores_por_equipo(self, equipo_id: UUID, skip: int = 0, limit: int = 100) -> List[JugadorResponse]:
        """List all players from a specific NFL team"""
        # Validate NFL team exists
        equipo = equipo_repository.get(equipo_id)
        if not equipo:
            raise NotFoundError("Equipo NFL no encontrado")
        
        jugadores = jugador_repository.get_by_equipo(equipo_id, skip, limit)
        return [_to_jugador_response(jugador) for jugador in jugadores]
    
    def listar_jugadores_por_posicion(self, posicion: str, skip: int = 0, limit: int = 100) -> List[JugadorResponse]:
        """List all players by position"""
        from models.database_models import PosicionJugadorEnum
        
        try:
            posicion_enum = PosicionJugadorEnum(posicion)
        except ValueError:
            raise ValidationError("Posición inválida")
        
        jugadores = jugador_repository.get_by_posicion(posicion_enum, skip, limit)
        return [_to_jugador_response(jugador) for jugador in jugadores]
    
    def listar_jugadores_por_liga(self, liga_id: UUID, skip: int = 0, limit: int = 100) -> List[JugadorResponse]:
        """List all players from teams in a specific league"""
        # Validate league exists (using validation_service if available)
        try:
            validation_service.validate_liga_exists(liga_id)
        except:
            # Fallback validation
            from repositories.liga_repository import liga_repository
            liga = liga_repository.get(liga_id)
            if not liga:
                raise NotFoundError("Liga no encontrada")
        
        jugadores = jugador_repository.get_by_liga_id(liga_id, skip, limit)
        return [_to_jugador_response(jugador) for jugador in jugadores]
    
    def listar_jugadores_por_usuario(self, usuario_id: UUID, skip: int = 0, limit: int = 100) -> List[JugadorResponse]:
        """List all players from teams owned by a specific user"""
        # Validate user exists (using validation_service if available)
        try:
            validation_service.validate_usuario_exists(usuario_id)
        except:
            # Fallback validation
            from repositories.usuario_repository import usuario_repository
            usuario = usuario_repository.get(usuario_id)
            if not usuario:
                raise NotFoundError("Usuario no encontrado")
        
        jugadores = jugador_repository.get_by_usuario_id(usuario_id, skip, limit)
        return [_to_jugador_response(jugador) for jugador in jugadores]
    
    def _convert_bulk_to_create(self, jugador_bulk: JugadorBulkCreate, equipo_cache: dict) -> JugadorCreate:
        """Convert JugadorBulkCreate to JugadorCreate with team lookup"""
        # Get or cache the NFL team by name
        if jugador_bulk.equipo_nfl not in equipo_cache:
            equipo = equipo_repository.get_by_nombre(jugador_bulk.equipo_nfl)
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

    def crear_jugadores_bulk(self, jugadores_data: List[JugadorBulkCreate], filename: Optional[str] = None) -> JugadorBulkResult:
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
                jugador_create = self._convert_bulk_to_create(jugador_bulk, equipo_cache)
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
        
        # Step 3: Process images and prepare data for all players
        players_to_create = []
        try:
            for jugador_create in validated_players:
                # Save image and generate thumbnail
                saved_image_path, saved_thumbnail_path = cdn_service.save_image_auto(
                    jugador_create.imagen_url,
                    entity_type="jugador"
                )
                
                # Update paths to local storage
                jugador_create.imagen_url = saved_image_path
                jugador_create.thumbnail_url = saved_thumbnail_path
                players_to_create.append(jugador_create)
                
        except ValueError as e:
            return JugadorBulkResult(
                success=False,
                created_count=0,
                error_count=1,
                errors=[f"Error al procesar imágenes: {str(e)}"],
                processed_file=self._move_processed_file(filename, success=False) if filename else None
            )
        
        # Step 4: Create all players in a single transaction
        try:
            from repositories.db_context import db_context
            
            with db_context.get_session() as db:
                created_players = []
                
                for jugador_create in players_to_create:
                    # Create player directly in the transaction
                    db_jugador = jugador_repository.create(jugador_create)
                    created_players.append(db_jugador)
                
                # Transaction will be committed automatically when context exits
            
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