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
    
    @handle_db_errors
    def create(self, db: Session, jugador_data: JugadorCreate) -> JugadorResponse:
        """Create a new jugador with validations"""
        # Validate input data
        if not jugador_data.nombre or not jugador_data.nombre.strip():
            raise ValidationError("El nombre del jugador es requerido")
        
        if not jugador_data.email or not validation_service.is_valid_email(jugador_data.email):
            raise ValidationError("Email inválido")
        
        if jugador_data.dorsal is not None and jugador_data.dorsal <= 0:
            raise ValidationError("El dorsal debe ser mayor que 0")
        
        # Check if team exists
        equipo = equipo_repository.get_by_id(db, jugador_data.equipo_nfl_id)
        if not equipo:
            raise NotFoundError("Equipo NFL no encontrado")
        
        # Check for existing dorsal in team
        if jugador_data.dorsal:
            existing_jugador = jugador_repository.get_by_team_and_dorsal(
                db, jugador_data.equipo_nfl_id, jugador_data.dorsal
            )
            if existing_jugador:
                raise ConflictError(f"El dorsal {jugador_data.dorsal} ya existe en este equipo")
        
        # Check for existing email
        existing_email = jugador_repository.get_by_email(db, jugador_data.email)
        if existing_email:
            raise ConflictError("Email ya registrado")
        
        # Create jugador
        db_jugador = jugador_repository.create(db, jugador_data)
        return self._to_response(db_jugador)
    
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
        created_players = []
        
        # Validate all players first (before creating any)
        equipo_cache = {}  # Cache to avoid repeated DB queries
        
        # Step 1: Validation phase
        for i, jugador_data in enumerate(jugadores_data):
            try:
                # Validate required fields (nombre, posicion, equipo_nfl, imagen)
                if not jugador_data.nombre:
                    errors.append(f"Jugador {i+1}: Campo 'nombre' es requerido")
                    continue
                
                if not jugador_data.posicion:
                    errors.append(f"Jugador {i+1}: Campo 'posicion' es requerido")
                    continue
                    
                if not jugador_data.equipo_nfl:
                    errors.append(f"Jugador {i+1}: Campo 'equipo_nfl' es requerido")
                    continue
                    
                if not jugador_data.imagen:
                    errors.append(f"Jugador {i+1}: Campo 'imagen' es requerido")
                    continue
                
                # Get or find NFL team by name
                equipo_nfl = None
                if jugador_data.equipo_nfl in equipo_cache:
                    equipo_nfl = equipo_cache[jugador_data.equipo_nfl]
                else:
                    # Search for team by name (case-insensitive)
                    equipo_nfl = equipo_repository.get_by_nombre(db, jugador_data.equipo_nfl)
                    if equipo_nfl:
                        equipo_cache[jugador_data.equipo_nfl] = equipo_nfl
                
                if not equipo_nfl:
                    errors.append(f"Jugador {i+1} ({jugador_data.nombre}): Equipo NFL '{jugador_data.equipo_nfl}' no encontrado")
                    continue
                
                # Check if player name already exists in team
                existing_player = jugador_repository.get_by_nombre_equipo(db, jugador_data.nombre, equipo_nfl.id)
                if existing_player:
                    errors.append(f"Jugador {i+1} ({jugador_data.nombre}): Ya existe un jugador con ese nombre en el equipo {jugador_data.equipo_nfl}")
                    continue
                
                # Validate image URL format (basic validation)
                if not jugador_data.imagen.startswith(('http://', 'https://')):
                    errors.append(f"Jugador {i+1} ({jugador_data.nombre}): URL de imagen debe comenzar con http:// o https://")
                    continue
                
                # Position validation is handled by Pydantic automatically
                # If we reach this point, the position is already valid
                
                # If we get here, the player data is valid
                prepared_player = {
                    'nombre': jugador_data.nombre.strip(),
                    'posicion': jugador_data.posicion,
                    'equipo_id': equipo_nfl.id,
                    'imagen_url': jugador_data.imagen.strip(),
                    'thumbnail_url': self._generate_thumbnail_url(jugador_data.imagen.strip()),
                    'activo': True  # All players created as active by default
                }
                created_players.append(prepared_player)
                
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
        
        # Step 3: Create all players in a single transaction
        try:
            created_count = 0
            for player_data in created_players:
                nuevo_jugador = JugadoresDB(**player_data)
                db.add(nuevo_jugador)
                created_count += 1
            
            db.commit()
            
            # Move file to processed folder on success
            processed_file = self._move_processed_file(filename, success=True) if filename else None
            
            return JugadorBulkResult(
                success=True,
                created_count=created_count,
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