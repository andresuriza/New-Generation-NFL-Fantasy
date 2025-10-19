from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.database_models import LigaDB
from models.liga import LigaResponse, LigaCreate

def _to_response(e: LigaDB) -> LigaResponse:
    return LigaResponse.model_validate(e, from_attributes=True)

class LigaService:
    # Revisar si se puede tener liga con mismo id, nombre
    def crear_liga(self, db: Session, liga: LigaCreate) -> LigaResponse:
        exists_liga = (db.query(LigaDB)
        .filter(LigaDB.nombre == liga.nombre)
        .first()
        )

        if exists_liga:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Esta liga ya existe",
            )

        nuevo =  LigaDB(
            nombre = liga.nombre
        )
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return _to_response(nuevo)

    def listar(self, db: Session) -> List[LigaResponse]:
        items = db.query(LigaDB).all()
        return [LigaResponse.model_validate(i, from_attributes=True) for i in items]

    def obtener(self, db: Session, liga_id: UUID) -> LigaResponse:
        item = db.query(LigaDB).filter(LigaDB.id == liga_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Liga no encontrada")
        return LigaResponse.model_validate(item, from_attributes=True)


liga_service = LigaService()
