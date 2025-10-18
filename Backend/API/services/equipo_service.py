from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.equipo import EquipoCreate, EquipoUpdate, EquipoResponse
from models.database_models import EquipoDB


def _to_response(e: EquipoDB) -> EquipoResponse:
    return EquipoResponse.model_validate(e, from_attributes=True)


class EquipoService:
    def crear_equipo(self, db: Session, equipo: EquipoCreate) -> EquipoResponse:
        exists_user_team = (
            db.query(EquipoDB)
            .filter(EquipoDB.liga_id == equipo.liga_id, EquipoDB.usuario_id == equipo.usuario_id)
            .first()
        )
        if exists_user_team:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario ya tiene un equipo en esta liga",
            )

        exists_name = (
            db.query(EquipoDB)
            .filter(EquipoDB.liga_id == equipo.liga_id, EquipoDB.nombre.ilike(equipo.nombre))
            .first()
        )
        if exists_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un equipo con este nombre en la liga",
            )

        nuevo = EquipoDB(
            liga_id=equipo.liga_id,
            usuario_id=equipo.usuario_id,
            nombre=equipo.nombre,
            thumbnail=equipo.thumbnail,
        )
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return _to_response(nuevo)

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
