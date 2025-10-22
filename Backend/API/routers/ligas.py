from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import BaseModel

from models.liga import (
    LigaResponse, LigaCreate, LigaUpdate,
    LigaMiembroResponse, LigaConMiembros,
    LigaCuposResponse
)
from services.liga_service import liga_service
from database import get_db

router = APIRouter()

class UnirseRequest(BaseModel):
    usuario_id: UUID
    contrasena: str
    alias: str

@router.post("/", response_model=LigaResponse, status_code=status.HTTP_201_CREATED)
async def crear_liga(liga: LigaCreate, db: Session = Depends(get_db)):
    """Crear una nueva liga"""
    return liga_service.crear_liga(db, liga)

@router.get("/", response_model=List[LigaResponse])
async def listar_ligas(
    skip: int = Query(0, ge=0, description="Elementos a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Límite de elementos"),
    db: Session = Depends(get_db)
):
    """Listar todas las ligas con paginación"""
    return liga_service.listar_ligas(db, skip, limit)

@router.get("/disponibles", response_model=List[LigaCuposResponse])
async def listar_ligas_disponibles(db: Session = Depends(get_db)):
    """Listar ligas con cupos disponibles"""
    return liga_service.obtener_ligas_disponibles(db)

@router.get("/{liga_id}", response_model=LigaResponse)
async def obtener_liga(liga_id: UUID, db: Session = Depends(get_db)):
    """Obtener una liga por ID"""
    return liga_service.obtener_liga(db, liga_id)

@router.get("/{liga_id}/completa", response_model=LigaConMiembros)
async def obtener_liga_completa(liga_id: UUID, db: Session = Depends(get_db)):
    """Obtener liga con sus miembros"""
    return liga_service.obtener_liga_con_miembros(db, liga_id)

@router.put("/{liga_id}", response_model=LigaResponse)
async def actualizar_liga(
    liga_id: UUID,
    actualizacion: LigaUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar una liga (solo en estado Pre_draft)"""
    return liga_service.actualizar_liga(db, liga_id, actualizacion)

@router.delete("/{liga_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_liga(liga_id: UUID, db: Session = Depends(get_db)):
    """Eliminar una liga (solo en estado Pre_draft)"""
    liga_service.eliminar_liga(db, liga_id)

@router.post("/{liga_id}/unirse", response_model=LigaMiembroResponse, status_code=status.HTTP_201_CREATED)
async def unirse_liga(
    liga_id: UUID,
    request: UnirseRequest,
    db: Session = Depends(get_db)
):
    """Unirse a una liga"""
    return liga_service.unirse_liga(
        db, liga_id, request.usuario_id, request.contrasena, request.alias
    )
