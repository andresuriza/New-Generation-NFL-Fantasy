from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from uuid import UUID
from models.equipo import EquipoNFLCreate, EquipoNFLUpdate, EquipoNFLResponse, EquipoNFLConMedia
from services.equipo_service import equipo_service
from database import get_db

router = APIRouter()

@router.post("/", response_model=EquipoNFLResponse, status_code=status.HTTP_201_CREATED)
async def crear_equipo_nfl(equipo: EquipoNFLCreate):
    """Crear un nuevo equipo NFL"""
    return equipo_service.crear_equipo(equipo)

@router.get("/", response_model=List[EquipoNFLResponse])
async def obtener_equipos_nfl():
    """Obtener todos los equipos NFL"""
    return equipo_service.listar()

@router.get("/{equipo_id}", response_model=EquipoNFLResponse)
async def obtener_equipo_nfl(equipo_id: UUID):
    """Obtener un equipo NFL por ID"""
    return equipo_service.obtener(equipo_id)

@router.get("/{equipo_id}/con-media", response_model=EquipoNFLConMedia)
async def obtener_equipo_nfl_con_media(equipo_id: UUID):
    """Obtener un equipo NFL con información de media"""
    return equipo_service.obtener_con_media(equipo_id)

@router.put("/{equipo_id}", response_model=EquipoNFLResponse)
async def actualizar_equipo_nfl(equipo_id: UUID, equipo_update: EquipoNFLUpdate):
    """Actualizar un equipo NFL"""
    return equipo_service.actualizar(equipo_id, equipo_update)

@router.delete("/{equipo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_equipo_nfl(equipo_id: UUID):
    """Eliminar un equipo NFL"""
    equipo_service.eliminar(equipo_id)
    return