from fastapi import APIRouter, HTTPException, status, UploadFile, File
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from models.media import Media, MediaCreate, MediaUpdate, MediaResponse
from services.media_service import media_service

router = APIRouter()

media_db = {}  # deprecated local store; logic now in media_service

@router.post("/", response_model=MediaResponse, status_code=status.HTTP_201_CREATED)
async def crear_media(media: MediaCreate):
    """Crear un nuevo registro de media para un equipo"""
    return media_service.crear(media)

@router.get("/", response_model=List[MediaResponse])
async def obtener_media():
    """Obtener todos los registros de media"""
    return media_service.listar()

@router.get("/{equipo_id}", response_model=MediaResponse)
async def obtener_media_por_equipo(equipo_id: UUID):
    """Obtener el registro de media de un equipo específico"""
    return media_service.obtener(equipo_id)

@router.put("/{equipo_id}", response_model=MediaResponse)
async def actualizar_media(equipo_id: UUID, media_update: MediaUpdate):
    """Actualizar el registro de media de un equipo"""
    return media_service.actualizar(equipo_id, media_update)

@router.delete("/{equipo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_media(equipo_id: UUID):
    """Eliminar el registro de media de un equipo"""
    media_service.eliminar(equipo_id)
    return

@router.post("/upload/{equipo_id}", response_model=MediaResponse)
async def subir_imagen_equipo(equipo_id: UUID, file: UploadFile = File(...)):
    """Subir una imagen para un equipo"""
    # Validar tipo de archivo
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser una imagen"
        )
    return media_service.subir_imagen(equipo_id, file.filename)

@router.get("/equipos-con-media/", response_model=List[UUID])
async def obtener_equipos_con_media():
    """Obtener lista de IDs de equipos que tienen media asociada"""
    return media_service.equipos_con_media()

@router.post("/generar/{equipo_id}", response_model=MediaResponse)
async def generar_imagen_equipo(equipo_id: UUID):
    """Generar una imagen automáticamente para un equipo (usando IA o plantilla)"""
    return media_service.generar_imagen(equipo_id)