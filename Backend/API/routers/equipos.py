from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from models.equipo import EquipoCreate, EquipoUpdate, EquipoResponse
from services.equipo_service import equipo_service
from database import get_db

router = APIRouter()

def to_response(e):
    return e

@router.post("/", response_model=EquipoResponse, status_code=status.HTTP_201_CREATED)
async def crear_equipo(equipo: EquipoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo equipo"""
    return equipo_service.crear_equipo(db, equipo)

@router.get("/", response_model=List[EquipoResponse])
async def obtener_equipos(db: Session = Depends(get_db)):
    return equipo_service.listar(db)

@router.get("/{equipo_id}", response_model=EquipoResponse)
async def obtener_equipo(equipo_id: UUID, db: Session = Depends(get_db)):
    return equipo_service.obtener(db, equipo_id)

@router.put("/{equipo_id}", response_model=EquipoResponse)
async def actualizar_equipo(equipo_id: UUID, equipo_update: EquipoUpdate, db: Session = Depends(get_db)):
    return equipo_service.actualizar(db, equipo_id, equipo_update)

@router.delete("/{equipo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_equipo(equipo_id: UUID, db: Session = Depends(get_db)):
    equipo_service.eliminar(db, equipo_id)
    return

@router.get("/liga/{liga_id}", response_model=List[EquipoResponse])
async def obtener_equipos_por_liga(liga_id: UUID, db: Session = Depends(get_db)):
    return equipo_service.listar_por_liga(db, liga_id)

@router.get("/usuario/{usuario_id}", response_model=List[EquipoResponse])
async def obtener_equipos_por_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    return equipo_service.listar_por_usuario(db, usuario_id)

@router.get("/liga/{liga_id}/usuario/{usuario_id}", response_model=EquipoResponse)
async def obtener_equipo_por_liga_y_usuario(liga_id: UUID, usuario_id: UUID, db: Session = Depends(get_db)):
    return equipo_service.obtener_por_liga_y_usuario(db, liga_id, usuario_id)