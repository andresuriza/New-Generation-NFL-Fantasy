from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from uuid import UUID

from models.liga import LigaResponse, LigaCreate
from services.liga_service import liga_service
from database import get_db

router = APIRouter()

@router.post("/", response_model=LigaResponse, status_code=status.HTTP_201_CREATED)
async def crear_liga(liga: LigaCreate, db: Session = Depends(get_db)):
    return liga_service.crear_liga(db, liga)

@router.get("/", response_model=List[LigaResponse])
async def listar_ligas(db: Session = Depends(get_db)):
    return liga_service.listar(db)


@router.get("/{liga_id}", response_model=LigaResponse)
async def obtener_liga(liga_id: UUID, db: Session = Depends(get_db)):
    return liga_service.obtener(db, liga_id)
