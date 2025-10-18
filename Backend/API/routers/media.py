from fastapi import APIRouter, HTTPException, status, UploadFile, File
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from models.media import Media, MediaCreate, MediaUpdate, MediaResponse

router = APIRouter()

# Simulación de base de datos en memoria
media_db = {}

@router.post("/", response_model=MediaResponse, status_code=status.HTTP_201_CREATED)
async def crear_media(media: MediaCreate):
    """Crear un nuevo registro de media para un equipo"""
    
    # Verificar si ya existe media para este equipo (PK constraint)
    if media.equipo_id in media_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un registro de media para este equipo"
        )
    
    # Crear el registro de media
    now = datetime.now()
    nuevo_media = Media(
        equipo_id=media.equipo_id,
        url=media.url,
        generado_en=now,
        creado_en=now
    )
    
    media_db[media.equipo_id] = nuevo_media
    return MediaResponse.from_orm(nuevo_media)

@router.get("/", response_model=List[MediaResponse])
async def obtener_media():
    """Obtener todos los registros de media"""
    return [MediaResponse.from_orm(media) for media in media_db.values()]

@router.get("/{equipo_id}", response_model=MediaResponse)
async def obtener_media_por_equipo(equipo_id: UUID):
    """Obtener el registro de media de un equipo específico"""
    if equipo_id not in media_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró media para este equipo"
        )
    return MediaResponse.from_orm(media_db[equipo_id])

@router.put("/{equipo_id}", response_model=MediaResponse)
async def actualizar_media(equipo_id: UUID, media_update: MediaUpdate):
    """Actualizar el registro de media de un equipo"""
    if equipo_id not in media_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró media para este equipo"
        )
    
    media_actual = media_db[equipo_id]
    
    # Actualizar solo los campos proporcionados
    update_data = media_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(media_actual, field, value)
    
    # Actualizar fecha de generación si se cambió la URL
    if "url" in update_data:
        media_actual.generado_en = datetime.now()
    
    media_db[equipo_id] = media_actual
    return MediaResponse.from_orm(media_actual)

@router.delete("/{equipo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_media(equipo_id: UUID):
    """Eliminar el registro de media de un equipo"""
    if equipo_id not in media_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró media para este equipo"
        )
    
    del media_db[equipo_id]
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
    
    # En una implementación real, aquí se guardaría el archivo en un sistema de almacenamiento
    # como AWS S3, Google Cloud Storage, o el sistema de archivos local
    # y se devolvería la URL del archivo guardado
    
    # Por ahora, simularemos que la imagen se guardó exitosamente
    imagen_url = f"/media/equipos/{equipo_id}/{file.filename}"
    
    # Crear o actualizar el registro de media
    now = datetime.now()
    if equipo_id in media_db:
        # Actualizar registro existente
        media_db[equipo_id].url = imagen_url
        media_db[equipo_id].generado_en = now
    else:
        # Crear nuevo registro
        nuevo_media = Media(
            equipo_id=equipo_id,
            url=imagen_url,
            generado_en=now,
            creado_en=now
        )
        media_db[equipo_id] = nuevo_media
    
    return MediaResponse.from_orm(media_db[equipo_id])

@router.get("/equipos-con-media/", response_model=List[UUID])
async def obtener_equipos_con_media():
    """Obtener lista de IDs de equipos que tienen media asociada"""
    return list(media_db.keys())

@router.post("/generar/{equipo_id}", response_model=MediaResponse)
async def generar_imagen_equipo(equipo_id: UUID):
    """Generar una imagen automáticamente para un equipo (usando IA o plantilla)"""
    
    # En una implementación real, aquí se generaría una imagen usando:
    # - Servicios de IA como DALL-E, Midjourney, etc.
    # - Plantillas predefinidas
    # - Generación procedural
    
    # Por ahora, simularemos la generación
    now = datetime.now()
    imagen_generada_url = f"/media/equipos/{equipo_id}/generated_{int(now.timestamp())}.png"
    
    if equipo_id in media_db:
        # Actualizar registro existente
        media_db[equipo_id].url = imagen_generada_url
        media_db[equipo_id].generado_en = now
    else:
        # Crear nuevo registro
        nuevo_media = Media(
            equipo_id=equipo_id,
            url=imagen_generada_url,
            generado_en=now,
            creado_en=now
        )
        media_db[equipo_id] = nuevo_media
    
    return MediaResponse.from_orm(media_db[equipo_id])