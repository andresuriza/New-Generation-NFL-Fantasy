"""
Business logic service for NFL Equipo operations
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.equipo import EquipoNFLCreate, EquipoNFLUpdate, EquipoNFLResponse, EquipoNFLConMedia
from models.database_models import EquipoDB
from repositories.equipo_repository import equipo_repository

def _to_response(e: EquipoDB) -> EquipoNFLResponse:
    """Convert EquipoDB to response model"""
    return EquipoNFLResponse.model_validate(e, from_attributes=True)

def _to_response_con_media(e: EquipoDB) -> EquipoNFLConMedia:
    """Convert EquipoDB to response with media"""
    media_url = e.media.url if e.media else None
    response_data = EquipoNFLResponse.model_validate(e, from_attributes=True).model_dump()
    response_data['media_url'] = media_url
    return EquipoNFLConMedia(**response_data)


class EquipoNFLService:
    """Service for NFL Team CRUD operations"""
    
    def crear_equipo(self, db: Session, equipo: EquipoNFLCreate) -> EquipoNFLResponse:
        """Create a new NFL team"""
        # Check if team name already exists
        existing_team = equipo_repository.get_by_nombre(db, equipo.nombre)
        if existing_team:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El equipo NFL '{equipo.nombre}' ya existe"
            )
        
        nuevo_equipo = equipo_repository.create(db, equipo)
        return _to_response(nuevo_equipo)

    def listar(self, db: Session) -> List[EquipoNFLResponse]:
        """List all NFL teams"""
        items = db.query(EquipoDB).all()
        return [_to_response(e) for e in items]

    def obtener(self, db: Session, equipo_id: UUID) -> EquipoNFLResponse:
        """Get NFL team by ID"""
        equipo = equipo_repository.get(db, equipo_id)
        if not equipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipo NFL no encontrado"
            )
        return _to_response(equipo)

    def obtener_con_media(self, db: Session, equipo_id: UUID) -> EquipoNFLConMedia:
        """Get NFL team by ID with media information"""
        equipo = equipo_repository.get(db, equipo_id)
        if not equipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipo NFL no encontrado"
            )
        return _to_response_con_media(equipo)

    def actualizar(self, db: Session, equipo_id: UUID, equipo_update: EquipoNFLUpdate) -> EquipoNFLResponse:
        """Update NFL team"""
        equipo_existente = equipo_repository.get(db, equipo_id)
        if not equipo_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipo NFL no encontrado"
            )
        
        # Check if new name already exists (if name is being changed)
        if equipo_update.nombre and equipo_update.nombre != equipo_existente.nombre:
            existing_team = equipo_repository.get_by_nombre(db, equipo_update.nombre)
            if existing_team:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El equipo NFL '{equipo_update.nombre}' ya existe"
                )
        
        equipo_actualizado = equipo_repository.update(db, equipo_id, equipo_update)
        return _to_response(equipo_actualizado)

    def eliminar(self, db: Session, equipo_id: UUID) -> None:
        """Delete NFL team"""
        equipo = equipo_repository.get(db, equipo_id)
        if not equipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipo NFL no encontrado"
            )
        
        # Check if team has players (should not delete if it has active relationships)
        if equipo.jugadores:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar el equipo NFL porque tiene jugadores asociados"
            )
        
        equipo_repository.delete(db, equipo_id)


# Create service instance
equipo_service = EquipoNFLService()
