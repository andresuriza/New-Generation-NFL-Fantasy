"""
FastAPI router for Equipos Fantasy (Fantasy Teams) endpoints
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query

from database import get_db
from models.equipo_fantasy import (
    EquipoFantasyCreate, EquipoFantasyUpdate, EquipoFantasyResponse, 
    EquipoFantasyConRelaciones, EquipoFantasyFilter, EquipoFantasyAuditResponse
)
from services.equipo_fantasy_service import equipo_fantasy_service
from routers.auth import get_current_user
from models.database_models import UsuarioDB

router = APIRouter(prefix="/equipos-fantasy", tags=["equipos-fantasy"])

@router.post("/", response_model=EquipoFantasyResponse, status_code=status.HTTP_201_CREATED)
async def crear_equipo_fantasy(
    equipo: EquipoFantasyCreate,
    current_user: UsuarioDB = Depends(get_current_user)
):
    """
    Crear un nuevo equipo fantasy.
    
    Validaciones:
    - El nombre debe ser único dentro de la liga (1-100 caracteres)
    - El usuario no puede tener más de un equipo por liga  
    - Si se proporciona imagen, debe ser JPEG/PNG, máximo 5MB, 300x300-1024x1024 píxeles
    - Se genera automáticamente un thumbnail de la imagen
    """
    return equipo_fantasy_service.crear_equipo_fantasy(equipo, current_user.id)

@router.get("/{equipo_id}", response_model=EquipoFantasyConRelaciones)
async def obtener_equipo_fantasy(
    equipo_id: UUID
):
    """Obtener equipo fantasy por ID con información de liga y usuario"""
    return equipo_fantasy_service.obtener_equipo_fantasy(equipo_id)

@router.put("/{equipo_id}", response_model=EquipoFantasyResponse)
async def actualizar_equipo_fantasy(
    equipo_id: UUID,
    equipo_update: EquipoFantasyUpdate,
    current_user: UsuarioDB = Depends(get_current_user)
):
    """
    Actualizar equipo fantasy (solo nombre e imagen).
    
    Solo el propietario del equipo puede editarlo.
    Se aplican las mismas validaciones que en creación.
    """
    return equipo_fantasy_service.actualizar_equipo_fantasy(equipo_id, equipo_update, current_user.id)

@router.delete("/{equipo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_equipo_fantasy(
    equipo_id: UUID,
    current_user: UsuarioDB = Depends(get_current_user)
):
    """Eliminar equipo fantasy. Solo el propietario puede eliminarlo."""
    equipo_fantasy_service.eliminar_equipo_fantasy(equipo_id, current_user.id)

@router.get("/", response_model=List[EquipoFantasyResponse])
async def listar_equipos_fantasy(
    liga_id: UUID = Query(None, description="Filtrar por liga"),
    usuario_id: UUID = Query(None, description="Filtrar por usuario"), 
    nombre: str = Query(None, description="Buscar por nombre (parcial)"),
    skip: int = Query(0, ge=0, description="Elementos a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Límite de elementos")
):
    """Listar equipos fantasy con filtros opcionales"""
    filtros = EquipoFantasyFilter(
        liga_id=liga_id,
        usuario_id=usuario_id,
        nombre=nombre
    )
    return equipo_fantasy_service.listar_equipos_fantasy(filtros, skip, limit)

@router.get("/liga/{liga_id}", response_model=List[EquipoFantasyResponse])
async def listar_equipos_por_liga(
    liga_id: UUID,
    skip: int = Query(0, ge=0, description="Elementos a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Límite de elementos")
):
    """Listar todos los equipos fantasy de una liga específica"""
    return equipo_fantasy_service.listar_equipos_por_liga(liga_id, skip, limit)

@router.get("/usuario/{usuario_id}", response_model=List[EquipoFantasyResponse])
async def listar_equipos_por_usuario(
    usuario_id: UUID,
    skip: int = Query(0, ge=0, description="Elementos a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Límite de elementos")
):
    """Listar todos los equipos fantasy de un usuario específico"""
    return equipo_fantasy_service.listar_equipos_por_usuario(usuario_id, skip, limit)

@router.get("/{equipo_id}/historial", response_model=List[EquipoFantasyAuditResponse])
async def obtener_historial_cambios(
    equipo_id: UUID,
    skip: int = Query(0, ge=0, description="Elementos a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Límite de elementos")
):
    """
    Obtener historial de cambios de un equipo fantasy.
    
    Muestra auditoría completa: quién hizo qué cambios y cuándo.
    """
    return equipo_fantasy_service.obtener_historial_cambios(equipo_id, skip, limit)

@router.get("/liga/{liga_id}/cambios-recientes", response_model=List[EquipoFantasyAuditResponse])
async def obtener_cambios_recientes_liga(
    liga_id: UUID,
    limit: int = Query(50, ge=1, le=100, description="Límite de elementos")
):
    """Obtener cambios recientes en todos los equipos fantasy de una liga"""
    return equipo_fantasy_service.obtener_cambios_recientes_liga(liga_id, limit)