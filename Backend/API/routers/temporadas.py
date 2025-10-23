from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from sqlalchemy.orm import Session
from uuid import UUID

from models.temporada import (
    TemporadaResponse, 
    TemporadaCreate, 
    TemporadaUpdate,
    TemporadaSemanaResponse,
    TemporadaSemanaCreate,
    TemporadaConSemanas
)
from services.temporada_service import temporada_service
from database import get_db

router = APIRouter()

@router.post("/", response_model=TemporadaResponse, status_code=status.HTTP_201_CREATED)
async def crear_temporada(temporada: TemporadaCreate, db: Session = Depends(get_db)):
    """Crear una nueva temporada"""
    return temporada_service.crear_temporada(db, temporada)

@router.get("/", response_model=List[TemporadaResponse])
async def listar_temporadas(db: Session = Depends(get_db)):
    """Listar todas las temporadas"""
    return temporada_service.listar_temporadas(db)

@router.get("/actual", response_model=TemporadaResponse)
async def obtener_temporada_actual(db: Session = Depends(get_db)):
    """Obtener la temporada actual"""
    return temporada_service.obtener_temporada_actual(db)

@router.get("/{temporada_id}", response_model=TemporadaResponse)
async def obtener_temporada(temporada_id: UUID, db: Session = Depends(get_db)):
    """Obtener una temporada por ID"""
    return temporada_service.obtener_temporada(db, temporada_id)

@router.get("/{temporada_id}/completa", response_model=TemporadaConSemanas)
async def obtener_temporada_completa(temporada_id: UUID, db: Session = Depends(get_db)):
    """Obtener temporada con todas sus semanas"""
    return temporada_service.obtener_temporada_con_semanas(db, temporada_id)

@router.put("/{temporada_id}", response_model=TemporadaResponse)
async def actualizar_temporada(
    temporada_id: UUID, 
    actualizacion: TemporadaUpdate, 
    db: Session = Depends(get_db)
):
    """Actualizar una temporada"""
    return temporada_service.actualizar_temporada(db, temporada_id, actualizacion)

@router.delete("/{temporada_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_temporada(temporada_id: UUID, db: Session = Depends(get_db)):
    """Eliminar una temporada"""
    temporada_service.eliminar_temporada(db, temporada_id)

@router.post("/semanas", response_model=TemporadaSemanaResponse, status_code=status.HTTP_201_CREATED)
async def crear_semana(semana: TemporadaSemanaCreate, db: Session = Depends(get_db)):
    """Crear una semana para una temporada"""
    return temporada_service.crear_semana(db, semana)