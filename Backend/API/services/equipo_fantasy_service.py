"""
Business logic service for Equipos Fantasy (Fantasy Teams) operations
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
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

def _validate_image_requirements(imagen_url: str) -> None:
    """Validate image format (basic validation - detailed validation should be done at upload time)"""
    if not imagen_url or not imagen_url.strip():
        return
    
    # Validate format
    if not re.match(r'.*\.(jpg|jpeg|png)(\?.*)?$', imagen_url, re.IGNORECASE):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La imagen debe ser formato JPEG o PNG"
        )
    
    # Note: Size and dimension validation should be implemented at image upload time
    # This is a basic URL format validation only

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
    
    def crear_equipo_fantasy(self, db: Session, equipo: EquipoFantasyCreate, usuario_id: UUID) -> EquipoFantasyResponse:
        """Create a new fantasy team"""
        
        # Validate league exists
        liga = liga_repository.get(db, equipo.liga_id)
        if not liga:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Liga no encontrada"
            )
        
        # Validate user exists
        usuario = usuario_repository.get(db, usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Check if user already has a team in this league
        equipo_existente = equipo_fantasy_repository.get_by_liga_and_usuario(db, equipo.liga_id, usuario_id)
        if equipo_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario ya tiene un equipo en esta liga"
            )
        
        # Check if team name is unique in league
        if equipo_fantasy_repository.exists_nombre_in_liga(db, equipo.liga_id, equipo.nombre):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un equipo con este nombre en la liga"
            )
        
        # Validate image if provided
        if equipo.imagen_url:
            _validate_image_requirements(equipo.imagen_url)
        
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
        
        return _to_equipo_fantasy_response(equipo_fantasy_repository.create(db, db_equipo))
    
    def obtener_equipo_fantasy(self, db: Session, equipo_id: UUID) -> EquipoFantasyConRelaciones:
        """Get fantasy team by ID with relationships"""
        equipo = equipo_fantasy_repository.get_with_relations(db, equipo_id)
        if not equipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipo fantasy no encontrado"
            )
        return _to_equipo_fantasy_con_relaciones_response(equipo)
    
    def actualizar_equipo_fantasy(self, db: Session, equipo_id: UUID, equipo_update: EquipoFantasyUpdate, usuario_id: UUID) -> EquipoFantasyResponse:
        """Update fantasy team"""
        equipo = equipo_fantasy_repository.get(db, equipo_id)
        if not equipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipo fantasy no encontrado"
            )
        
        # Check ownership
        if equipo.usuario_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para modificar este equipo"
            )
        
        update_data = {}
        
        # Validate and update name
        if equipo_update.nombre is not None:
            if equipo_fantasy_repository.exists_nombre_in_liga(db, equipo.liga_id, equipo_update.nombre, equipo_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un equipo con este nombre en la liga"
                )
            update_data['nombre'] = equipo_update.nombre
        
        # Validate and update image
        if equipo_update.imagen_url is not None:
            if equipo_update.imagen_url.strip():
                _validate_image_requirements(equipo_update.imagen_url)
                update_data['imagen_url'] = equipo_update.imagen_url
                update_data['thumbnail_url'] = _generate_thumbnail_url(equipo_update.imagen_url)
            else:
                update_data['imagen_url'] = None
                update_data['thumbnail_url'] = None
        
        return _to_equipo_fantasy_response(equipo_fantasy_repository.update(db, equipo_id, update_data))
    
    def eliminar_equipo_fantasy(self, db: Session, equipo_id: UUID, usuario_id: UUID) -> bool:
        """Delete fantasy team"""
        equipo = equipo_fantasy_repository.get(db, equipo_id)
        if not equipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipo fantasy no encontrado"
            )
        
        # Check ownership
        if equipo.usuario_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para eliminar este equipo"
            )
        
        return equipo_fantasy_repository.delete(db, equipo_id)
    
    def listar_equipos_fantasy(self, db: Session, filtros: EquipoFantasyFilter, skip: int = 0, limit: int = 100) -> List[EquipoFantasyResponse]:
        """List fantasy teams with filters"""
        equipos = equipo_fantasy_repository.search_with_filter(db, filtros, skip, limit)
        return [_to_equipo_fantasy_response(equipo) for equipo in equipos]
    
    def listar_equipos_por_liga(self, db: Session, liga_id: UUID, skip: int = 0, limit: int = 100) -> List[EquipoFantasyResponse]:
        """List fantasy teams by league"""
        equipos = equipo_fantasy_repository.get_by_liga(db, liga_id, skip, limit)
        return [_to_equipo_fantasy_response(equipo) for equipo in equipos]
    
    def listar_equipos_por_usuario(self, db: Session, usuario_id: UUID, skip: int = 0, limit: int = 100) -> List[EquipoFantasyResponse]:
        """List fantasy teams by user"""
        equipos = equipo_fantasy_repository.get_by_usuario(db, usuario_id, skip, limit)
        return [_to_equipo_fantasy_response(equipo) for equipo in equipos]
    
    def obtener_historial_cambios(self, db: Session, equipo_id: UUID, skip: int = 0, limit: int = 100) -> List[EquipoFantasyAuditResponse]:
        """Get audit history for a fantasy team"""
        # Check if team exists
        if not equipo_fantasy_repository.get(db, equipo_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipo fantasy no encontrado"
            )
        
        audits = equipo_fantasy_audit_repository.get_by_equipo_fantasy(db, equipo_id, skip, limit)
        return [_to_audit_response(audit) for audit in audits]
    
    def obtener_cambios_recientes_liga(self, db: Session, liga_id: UUID, limit: int = 50) -> List[EquipoFantasyAuditResponse]:
        """Get recent changes for all fantasy teams in a league"""
        # Check if league exists
        if not liga_repository.get(db, liga_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Liga no encontrada"
            )
        
        audits = equipo_fantasy_audit_repository.get_recent_changes(db, liga_id, limit)
        return [_to_audit_response(audit) for audit in audits]

# Service instance
equipo_fantasy_service = EquipoFantasyService()