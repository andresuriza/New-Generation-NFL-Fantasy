from fastapi import APIRouter, HTTPException, status, UploadFile, File, Depends
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from models.media import MediaCreate, MediaUpdate, MediaResponse
from services.media_service import media_service
from database import get_db

router = APIRouter()

@router.post("/", response_model=MediaResponse, status_code=status.HTTP_201_CREATED)
async def crear_media(media: MediaCreate, db: Session = Depends(get_db)):
    """Crear un nuevo registro de media para un equipo"""
    try:
        return media_service.crear(db, media)
    except ValueError as e:
        error_msg = str(e)
        if "no encontrado" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        elif "Ya existe" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

@router.get("/", response_model=List[MediaResponse])
async def obtener_media(limit: int = 100, db: Session = Depends(get_db)):
    """Obtener todos los registros de media"""
    return media_service.listar(db, limit)

@router.get("/{equipo_id}", response_model=MediaResponse)
async def obtener_media_por_equipo(equipo_id: UUID, db: Session = Depends(get_db)):
    """Obtener el registro de media de un equipo específico"""
    result = media_service.obtener(db, equipo_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró media para este equipo"
        )
    return result

@router.put("/{equipo_id}", response_model=MediaResponse)
async def actualizar_media(equipo_id: UUID, media_update: MediaUpdate, db: Session = Depends(get_db)):
    """Actualizar el registro de media de un equipo"""
    result = media_service.actualizar(db, equipo_id, media_update)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró media para este equipo"
        )
    return result

@router.delete("/{equipo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_media(equipo_id: UUID, db: Session = Depends(get_db)):
    """Eliminar el registro de media de un equipo"""
    success = media_service.eliminar(db, equipo_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró media para este equipo"
        )

@router.post("/upload/{equipo_id}", response_model=MediaResponse)
async def subir_imagen_equipo(equipo_id: UUID, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Subir una imagen para un equipo"""
    # Validar tipo de archivo
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser una imagen"
        )
    return media_service.subir_imagen(db, equipo_id, file.filename)

@router.get("/equipos-con-media/", response_model=List[UUID])
async def obtener_equipos_con_media(db: Session = Depends(get_db)):
    """Obtener lista de IDs de equipos que tienen media asociada"""
    return media_service.equipos_con_media(db)

@router.post("/generar/{equipo_id}", response_model=MediaResponse)
async def generar_imagen_equipo(equipo_id: UUID, db: Session = Depends(get_db)):
    """Generar una imagen automáticamente para un equipo (usando IA o plantilla)"""
    return media_service.generar_imagen(db, equipo_id)