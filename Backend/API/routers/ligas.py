from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import BaseModel

from models.liga import (
    LigaResponse, LigaCreate, LigaUpdate,
    LigaMiembroResponse, LigaConMiembros, LigaFilter
)
from services.liga_service import liga_service
from database import get_db

router = APIRouter()

class LigaCreateResponse(BaseModel):
    """Response for league creation including available slots"""
    liga: LigaResponse
    cupos_disponibles: int
    equipos_max: int
    miembros_actuales: int

class UnirseRequest(BaseModel):
    usuario_id: UUID
    contrasena: str
    alias: str
    nombre_equipo: str

@router.post("/", response_model=LigaCreateResponse, status_code=status.HTTP_201_CREATED)
async def crear_liga(liga: LigaCreate, db: Session = Depends(get_db)):
    """
    Crear una nueva liga.
    """
    try:
        liga_creada = liga_service.crear_liga(db, liga)
        info_cupos = liga_service.obtener_info_cupos(db, liga_creada.id)
        
        return LigaCreateResponse(
            liga=liga_creada,
            cupos_disponibles=info_cupos["cupos_disponibles"],
            equipos_max=info_cupos["equipos_max"],
            miembros_actuales=info_cupos["miembros_actuales"]
        )
    except ValueError as e:
        # Password validation and other business logic errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[LigaResponse])
async def listar_ligas(
    skip: int = Query(0, ge=0, description="Elementos a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Límite de elementos"),
    db: Session = Depends(get_db)
):
    """Listar todas las ligas con paginación"""
    return liga_service.listar_ligas(db, skip, limit)

@router.get("/buscar", response_model=List[LigaResponse])
async def buscar_ligas(
    nombre: Optional[str] = Query(None, description="Buscar por nombre (parcial)"),
    temporada_id: Optional[UUID] = Query(None, description="Filtrar por temporada"),
    estado: Optional[str] = Query(None, description="Filtrar por estado (Pre_draft, Draft)"),
    skip: int = Query(0, ge=0, description="Elementos a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Límite de elementos"),
    db: Session = Depends(get_db)
):
    """Buscar ligas con filtros"""
    filtros = LigaFilter(
        nombre=nombre,
        temporada_id=temporada_id,
        estado=estado
    )
    return liga_service.buscar_ligas(db, filtros, skip, limit)

@router.get("/{liga_id}", response_model=LigaResponse)
async def obtener_liga(liga_id: UUID, db: Session = Depends(get_db)):
    """Obtener una liga por ID"""
    return liga_service.obtener_liga(db, liga_id)

@router.get("/{liga_id}/completa", response_model=LigaConMiembros)
async def obtener_liga_completa(liga_id: UUID, db: Session = Depends(get_db)):
    """Obtener liga con sus miembros"""
    return liga_service.obtener_liga_con_miembros(db, liga_id)

@router.get("/{liga_id}/cupos", response_model=dict)
async def obtener_cupos_liga(liga_id: UUID, db: Session = Depends(get_db)):
    """
    Obtener información de cupos disponibles en la liga.
    
    """
    return liga_service.obtener_info_cupos(db, liga_id)

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
    try:
        return liga_service.unirse_liga(
            db, liga_id, request.usuario_id, request.contrasena, request.alias, request.nombre_equipo
        )
    except ValueError as e:
        error_msg = str(e)
        
        # Map specific business errors to appropriate HTTP status codes
        if "contraseña" in error_msg.lower() and "incorrecta" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_msg
            )
        elif "no eres miembro" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        elif "comisionado no puede" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_msg
            )
        else:
            # General business logic errors
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
