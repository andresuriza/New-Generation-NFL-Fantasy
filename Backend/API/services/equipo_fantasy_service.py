"""
Business logic service for Equipos Fantasy (Fantasy Teams) operations
"""
from typing import List, Optional
from uuid import UUID
import re

from models.database_models import EquipoFantasyDB, EquipoFantasyAuditDB
from models.equipo_fantasy import (
    EquipoFantasyCreate, EquipoFantasyUpdate, EquipoFantasyResponse, 
    EquipoFantasyConRelaciones, EquipoFantasyFilter, EquipoFantasyAuditResponse,
    LigaResponseBasic, UsuarioResponseBasic
)
from repositories.equipo_fantasy_repository import equipo_fantasy_repository, equipo_fantasy_audit_repository
from repositories.liga_repository import liga_repository
from repositories.usuario_repository import usuario_repository
from services.error_handling import handle_db_errors
from validators.equipo_fantasy_validator import EquipoFantasyValidator
from exceptions.business_exceptions import ValidationError, ConflictError, NotFoundError

def _to_equipo_fantasy_response(equipo: EquipoFantasyDB) -> EquipoFantasyResponse:
    return EquipoFantasyResponse.model_validate(equipo, from_attributes=True)

def _to_equipo_fantasy_con_relaciones_response(equipo: EquipoFantasyDB) -> EquipoFantasyConRelaciones:
    equipo_data = EquipoFantasyConRelaciones.model_validate(equipo, from_attributes=True)
    if equipo.liga:
        equipo_data.liga = LigaResponseBasic.model_validate(equipo.liga, from_attributes=True)
    if equipo.usuario:
        equipo_data.usuario = UsuarioResponseBasic.model_validate(equipo.usuario, from_attributes=True)
    return equipo_data

def _to_audit_response(audit: EquipoFantasyAuditDB) -> EquipoFantasyAuditResponse:
    audit_data = EquipoFantasyAuditResponse.model_validate(audit, from_attributes=True)
    if audit.usuario:
        audit_data.usuario = UsuarioResponseBasic.model_validate(audit.usuario, from_attributes=True)
    return audit_data

def _generate_thumbnail_url(imagen_url: Optional[str]) -> Optional[str]:
    """Generate thumbnail URL from image URL (placeholder implementation)"""
    if not imagen_url:
        return None
    
    # This is a placeholder implementation
    # In a real application, you would use an image processing service
    # like Cloudinary, AWS Lambda, or a custom service to generate thumbnails
    base_url = imagen_url.rsplit('.', 1)[0]
    extension = imagen_url.rsplit('.', 1)[1]
    return f"{base_url}_thumb.{extension}"

class EquipoFantasyService:
    """Service for Fantasy Team CRUD operations"""
    
    @handle_db_errors
    def crear_equipo_fantasy(self,  equipo: EquipoFantasyCreate, usuario_id: UUID) -> EquipoFantasyResponse:
        """Create a new fantasy team"""
        
        # Use validator for all validations
        validator = EquipoFantasyValidator()
        validator.validate_liga_exists(equipo.liga_id)
        validator.validate_usuario_exists(usuario_id)
        validator.validate_usuario_not_has_team_in_liga(usuario_id, equipo.liga_id)
        validator.validate_nombre_unique_in_liga(equipo.nombre, equipo.liga_id)
        
        # Validate image if provided
        if equipo.imagen_url:
            validator.validate_imagen_url_format(equipo.imagen_url)
        
        # Generate thumbnail
        thumbnail_url = _generate_thumbnail_url(equipo.imagen_url)
        
        # Create new fantasy team
        db_equipo = EquipoFantasyDB(
            nombre=equipo.nombre,
            liga_id=equipo.liga_id,
            usuario_id=usuario_id,
            imagen_url=equipo.imagen_url,
            thumbnail_url=thumbnail_url
        )
        
        return _to_equipo_fantasy_response(equipo_fantasy_repository.create(db_equipo))
    
    def obtener_equipo_fantasy(self, equipo_id: UUID) -> EquipoFantasyConRelaciones:
        """Get fantasy team by ID with relationships"""
        equipo = equipo_fantasy_repository.get_with_relations(equipo_id)
        if not equipo:
            raise NotFoundError("Equipo fantasy no encontrado")
        return _to_equipo_fantasy_con_relaciones_response(equipo)
    
    @handle_db_errors
    def actualizar_equipo_fantasy(self, equipo_id: UUID, equipo_update: EquipoFantasyUpdate, usuario_id: UUID) -> EquipoFantasyResponse:
        """Update fantasy team"""
        validator = EquipoFantasyValidator()
        equipo = validator.validate_exists(equipo_id)
        
        # Check ownership using validator
        validator.validate_usuario_owns_team(equipo, usuario_id)
        
        update_data = {}
        
        # Validate and update name
        if equipo_update.nombre is not None:
            validator.validate_nombre_unique_in_liga(equipo_update.nombre, equipo.liga_id, equipo_id)
            update_data['nombre'] = equipo_update.nombre
        
        # Validate and update image
        if equipo_update.imagen_url is not None:
            if equipo_update.imagen_url.strip():
                validator.validate_imagen_url_format(equipo_update.imagen_url)
                update_data['imagen_url'] = equipo_update.imagen_url
                update_data['thumbnail_url'] = _generate_thumbnail_url(equipo_update.imagen_url)
            else:
                update_data['imagen_url'] = None
                update_data['thumbnail_url'] = None
        
        return _to_equipo_fantasy_response(equipo_fantasy_repository.update(equipo_id, update_data))
    
    def eliminar_equipo_fantasy(self, equipo_id: UUID, usuario_id: UUID) -> bool:
        """Delete fantasy team"""
        validator = EquipoFantasyValidator()
        equipo = validator.validate_exists(equipo_id)
        
        # Check ownership using validator
        validator.validate_usuario_owns_team(equipo, usuario_id)
        
        return equipo_fantasy_repository.delete(equipo_id)
    
    def listar_equipos_fantasy(self,  filtros: EquipoFantasyFilter, skip: int = 0, limit: int = 100) -> List[EquipoFantasyResponse]:
        """List fantasy teams with filters"""
        equipos = equipo_fantasy_repository.search_with_filter(filtros, skip, limit)
        return [_to_equipo_fantasy_response(equipo) for equipo in equipos]
    
    def listar_equipos_por_liga(self, liga_id: UUID, skip: int = 0, limit: int = 100) -> List[EquipoFantasyResponse]:
        """List fantasy teams by league"""
        equipos = equipo_fantasy_repository.get_by_liga(liga_id, skip, limit)
        return [_to_equipo_fantasy_response(equipo) for equipo in equipos]
    
    def listar_equipos_por_usuario(self, usuario_id: UUID, skip: int = 0, limit: int = 100) -> List[EquipoFantasyResponse]:
        """List fantasy teams by user"""
        equipos = equipo_fantasy_repository.get_by_usuario(usuario_id, skip, limit)
        return [_to_equipo_fantasy_response(equipo) for equipo in equipos]
    
    def obtener_historial_cambios(self, equipo_id: UUID, skip: int = 0, limit: int = 100) -> List[EquipoFantasyAuditResponse]:
        """Get audit history for a fantasy team"""
        # Check if team exists
        if not equipo_fantasy_repository.get(equipo_id):
            raise NotFoundError("Equipo fantasy no encontrado")
        
        audits = equipo_fantasy_audit_repository.get_by_equipo_fantasy(equipo_id, skip, limit)
        return [_to_audit_response(audit) for audit in audits]
    
    def obtener_cambios_recientes_liga(self,  liga_id: UUID, limit: int = 50) -> List[EquipoFantasyAuditResponse]:
        """Get recent changes for all fantasy teams in a league"""
        # Check if league exists
        if not liga_repository.get(liga_id):
            raise NotFoundError("Liga no encontrada")
        
        audits = equipo_fantasy_audit_repository.get_recent_changes(liga_id, limit)
        return [_to_audit_response(audit) for audit in audits]

# Service instance
equipo_fantasy_service = EquipoFantasyService()