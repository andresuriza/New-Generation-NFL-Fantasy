"""
API Router for Jugadores (Players) endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID

from models.jugador import (
    JugadorResponse, JugadorCreate, JugadorUpdate, JugadorConEquipo, 
    JugadorFilter, JugadorBulkRequest, JugadorBulkResult
)
from models.database_models import PosicionJugadorEnum
from services.jugador_service import jugador_service
from database import get_db

router = APIRouter()

@router.post("/", response_model=JugadorResponse, status_code=status.HTTP_201_CREATED)
async def crear_jugador(jugador: JugadorCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo jugador.
    """
    return jugador_service.create(db, jugador)

@router.post("/bulk", response_model=JugadorBulkResult, status_code=status.HTTP_201_CREATED)
async def crear_jugadores_bulk(
    request: JugadorBulkRequest,
    db: Session = Depends(get_db)
):
    """
    Crear múltiples jugadores desde datos JSON.
    
    Características:
    • El JSON incluye: nombre, posición, equipo NFL, imagen, ID (opcional)
    • El thumbnail se autogenera de la imagen
    • Todos los jugadores creados quedan activos por defecto
    • Validación de formato y datos antes de procesar
    • Al final de la carga se genera un reporte de éxito y errores
    • Si existe al menos un error no se crea ninguno de los jugadores (operación todo-o-nada)
    • El archivo se mueve a un folder de archivos procesados con formato <timestamp>_<status>_<nombre>.json
    
    Comportamientos alternativos:
    • Si el nombre del jugador ya existe para el mismo equipo NFL, no se crea y se notifica
    • Si no se presentan todos los campos requeridos, no se crea y se notifica
    
    Args:
        request: Contiene la lista de jugadores y opcionalmente el nombre del archivo
        
    Returns:
        JugadorBulkResult con estadísticas de la operación
        
    Raises:
        HTTPException 400: Si hay errores en los datos
        HTTPException 500: Si hay errores en el procesamiento
    """
    return jugador_service.crear_jugadores_bulk(db, request.jugadores, request.filename)

@router.get("/", response_model=List[JugadorResponse])
async def listar_jugadores(
    skip: int = Query(0, ge=0, description="Elementos a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Límite de elementos"),
    db: Session = Depends(get_db)
):
    """Listar todos los jugadores con paginación"""
    return jugador_service.listar_jugadores(db, skip, limit)

@router.get("/buscar", response_model=List[JugadorResponse])
async def buscar_jugadores(
    posicion: Optional[PosicionJugadorEnum] = Query(None, description="Filtrar por posición"),
    equipo_id: Optional[UUID] = Query(None, description="Filtrar por equipo NFL"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    nombre: Optional[str] = Query(None, description="Buscar por nombre (parcial)"),
    skip: int = Query(0, ge=0, description="Elementos a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Límite de elementos"),
    db: Session = Depends(get_db)
):
    """Buscar jugadores con filtros"""
    filters = JugadorFilter(
        posicion=posicion,
        equipo_id=equipo_id,
        activo=activo,
        nombre=nombre
    )
    return jugador_service.buscar_jugadores(db, filters, skip, limit)

@router.get("/posicion/{posicion}", response_model=List[JugadorResponse])
async def listar_jugadores_por_posicion(
    posicion: PosicionJugadorEnum,
    skip: int = Query(0, ge=0, description="Elementos a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Límite de elementos"),
    db: Session = Depends(get_db)
):
    """Listar jugadores por posición"""
    return jugador_service.listar_jugadores_por_posicion(db, posicion.value, skip, limit)

@router.get("/equipo/{equipo_id}", response_model=List[JugadorResponse])
async def listar_jugadores_por_equipo(
    equipo_id: UUID,
    skip: int = Query(0, ge=0, description="Elementos a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Límite de elementos"),
    db: Session = Depends(get_db)
):
    """Listar jugadores de un equipo NFL específico"""
    return jugador_service.listar_jugadores_por_equipo(db, equipo_id, skip, limit)

@router.get("/liga/{liga_id}", response_model=List[JugadorResponse])
async def listar_jugadores_por_liga(
    liga_id: UUID,
    skip: int = Query(0, ge=0, description="Elementos a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Límite de elementos"),
    db: Session = Depends(get_db)
):
    """Listar todos los jugadores de equipos en una liga específica"""
    return jugador_service.listar_jugadores_por_liga(db, liga_id, skip, limit)

@router.get("/usuario/{usuario_id}", response_model=List[JugadorResponse])
async def listar_jugadores_por_usuario(
    usuario_id: UUID,
    skip: int = Query(0, ge=0, description="Elementos a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Límite de elementos"),
    db: Session = Depends(get_db)
):
    """Listar todos los jugadores de equipos propiedad de un usuario específico"""
    return jugador_service.listar_jugadores_por_usuario(db, usuario_id, skip, limit)

@router.get("/{jugador_id}", response_model=JugadorResponse)
async def obtener_jugador(jugador_id: UUID, db: Session = Depends(get_db)):
    """Obtener un jugador por ID"""
    return jugador_service.obtener_jugador(db, jugador_id)

@router.get("/{jugador_id}/completo", response_model=JugadorConEquipo)
async def obtener_jugador_completo(jugador_id: UUID, db: Session = Depends(get_db)):
    """Obtener jugador con información del equipo fantasy"""
    return jugador_service.obtener_jugador_con_equipo(db, jugador_id)

@router.put("/{jugador_id}", response_model=JugadorResponse)
async def actualizar_jugador(
    jugador_id: UUID,
    actualizacion: JugadorUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un jugador"""
    return jugador_service.actualizar_jugador(db, jugador_id, actualizacion)

@router.delete("/{jugador_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_jugador(jugador_id: UUID, db: Session = Depends(get_db)):
    """Eliminar un jugador"""
    jugador_service.eliminar_jugador(db, jugador_id)