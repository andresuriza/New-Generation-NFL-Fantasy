from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
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
async def crear_temporada(temporada: TemporadaCreate):
    """Crear una nueva temporada"""
    return temporada_service.crear_temporada(temporada)

@router.get("/", response_model=List[TemporadaResponse])
async def listar_temporadas():
    """Listar todas las temporadas"""
    return temporada_service.listar_temporadas()

@router.get("/actual", response_model=TemporadaResponse)
async def obtener_temporada_actual():
    """Obtener la temporada actual"""
    return temporada_service.obtener_temporada_actual()

@router.get("/{temporada_id}", response_model=TemporadaResponse)
async def obtener_temporada(temporada_id: UUID):
    """Obtener una temporada por ID"""
    return temporada_service.obtener_temporada(temporada_id)

@router.get("/{temporada_id}/completa", response_model=TemporadaConSemanas)
async def obtener_temporada_completa(temporada_id: UUID):
    """Obtener temporada con todas sus semanas"""
    return temporada_service.obtener_temporada_con_semanas(temporada_id)

@router.put("/{temporada_id}", response_model=TemporadaResponse)
async def actualizar_temporada(
    temporada_id: UUID, 
    actualizacion: TemporadaUpdate
):
    """Actualizar una temporada"""
    return temporada_service.actualizar_temporada(temporada_id, actualizacion)

@router.delete("/{temporada_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_temporada(temporada_id: UUID):
    """Eliminar una temporada"""
    temporada_service.eliminar_temporada(temporada_id)

@router.post("/semanas", response_model=TemporadaSemanaResponse, status_code=status.HTTP_201_CREATED)
async def crear_semana(semana: TemporadaSemanaCreate):
    """Crear una semana para una temporada"""
    return temporada_service.crear_semana(semana)