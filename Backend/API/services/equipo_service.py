"""
Business logic service for Equipo operations with separation of concerns
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.equipo import EquipoCreate, EquipoUpdate, EquipoResponse, EquipoConMedia
from models.database_models import EquipoDB
from repositories.equipo_repository import equipo_repository
from services.validation_service import validation_service

def _to_response(e: EquipoDB) -> EquipoResponse:
    return EquipoResponse.model_validate(e, from_attributes=True)

def _to_response_con_media(e: EquipoDB) -> EquipoConMedia:
    media_url = e.media.url if e.media else None
    response_data = EquipoResponse.model_validate(e, from_attributes=True).model_dump()
    response_data['media_url'] = media_url
    return EquipoConMedia(**response_data)


class EquipoService:
    """Service for Equipo CRUD operations"""
    
    def crear_equipo(self, db: Session, equipo: EquipoCreate) -> EquipoResponse:
        """Create a new team"""
        # Validate league and user exist
        validation_service.validate_liga_exists(db, equipo.liga_id)
        validation_service.validate_usuario_exists(db, equipo.usuario_id)
        
        # Validate user doesn't already have a team in this league
        existing_team = equipo_repository.get_by_liga_usuario(db, equipo.liga_id, equipo.usuario_id)
        if existing_team:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario ya tiene un equipo en esta liga"
            )
        
        # Validate team name is unique in league
        existing_name = equipo_repository.get_by_liga_nombre(db, equipo.liga_id, equipo.nombre)
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un equipo con este nombre en la liga"
            )
        
        nuevo_equipo = equipo_repository.create(db, equipo)
        return _to_response(nuevo_equipo)

    def listar(self, db: Session) -> List[EquipoResponse]:
        items = db.query(EquipoDB).all()
        return [_to_response(e) for e in items]

    def obtener(self, db: Session, equipo_id: UUID) -> EquipoResponse:
        e = db.query(EquipoDB).filter(EquipoDB.id == equipo_id).first()
        if not e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipo no encontrado")
        return _to_response(e)

    def actualizar(self, db: Session, equipo_id: UUID, equipo_update: EquipoUpdate) -> EquipoResponse:
        e = db.query(EquipoDB).filter(EquipoDB.id == equipo_id).first()
        if not e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipo no encontrado")

        data = equipo_update.model_dump(exclude_unset=True)
        target_liga_id = data.get("liga_id", e.liga_id)
        target_nombre = data.get("nombre", e.nombre)

        if target_liga_id != e.liga_id:
            exists_user_team = (
                db.query(EquipoDB)
                .filter(EquipoDB.liga_id == target_liga_id, EquipoDB.usuario_id == e.usuario_id)
                .first()
            )
            if exists_user_team:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El usuario ya tiene un equipo en la liga destino",
                )

        if "nombre" in data or ("liga_id" in data and target_liga_id != e.liga_id):
            conflict = (
                db.query(EquipoDB)
                .filter(
                    EquipoDB.id != equipo_id,
                    EquipoDB.liga_id == target_liga_id,
                    EquipoDB.nombre.ilike(target_nombre),
                )
                .first()
            )
            if conflict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un equipo con este nombre en la liga destino",
                )

        for k, v in data.items():
            setattr(e, k, v)

        db.commit()
        db.refresh(e)
        return _to_response(e)

    def eliminar(self, db: Session, equipo_id: UUID) -> None:
        e = db.query(EquipoDB).filter(EquipoDB.id == equipo_id).first()
        if not e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipo no encontrado")
        db.delete(e)
        db.commit()

    def listar_por_liga(self, db: Session, liga_id: UUID) -> List[EquipoResponse]:
        items = db.query(EquipoDB).filter(EquipoDB.liga_id == liga_id).all()
        return [_to_response(e) for e in items]

    def listar_por_usuario(self, db: Session, usuario_id: UUID) -> List[EquipoResponse]:
        items = db.query(EquipoDB).filter(EquipoDB.usuario_id == usuario_id).all()
        return [_to_response(e) for e in items]

    def obtener_por_liga_y_usuario(self, db: Session, liga_id: UUID, usuario_id: UUID) -> EquipoResponse:
        e = (
            db.query(EquipoDB)
            .filter(EquipoDB.liga_id == liga_id, EquipoDB.usuario_id == usuario_id)
            .first()
        )
        if not e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El usuario no tiene un equipo en esta liga",
            )
        return _to_response(e)


equipo_service = EquipoService()
