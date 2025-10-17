from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.database_models import LigaDB
from models.liga import LigaResponse


class LigaService:
    def listar(self, db: Session) -> List[LigaResponse]:
        items = db.query(LigaDB).all()
        return [LigaResponse.model_validate(i, from_attributes=True) for i in items]

    def obtener(self, db: Session, liga_id: UUID) -> LigaResponse:
        item = db.query(LigaDB).filter(LigaDB.id == liga_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Liga no encontrada")
        return LigaResponse.model_validate(item, from_attributes=True)


liga_service = LigaService()
