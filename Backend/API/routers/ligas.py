from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from uuid import UUID

from models.database_models import LigaDB
from models.liga import LigaResponse
from database import get_db

router = APIRouter()


@router.get("/", response_model=List[LigaResponse])
async def listar_ligas(db: Session = Depends(get_db)):
    items = db.query(LigaDB).all()
    return [LigaResponse.model_validate(i, from_attributes=True) for i in items]


@router.get("/{liga_id}", response_model=LigaResponse)
async def obtener_liga(liga_id: UUID, db: Session = Depends(get_db)):
    item = db.query(LigaDB).filter(LigaDB.id == liga_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Liga no encontrada")
    return LigaResponse.model_validate(item, from_attributes=True)
