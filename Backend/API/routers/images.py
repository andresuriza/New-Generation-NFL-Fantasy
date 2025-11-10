"""
Router for serving images (pictures and thumbnails)
"""
from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import FileResponse, Response
import os
from pathlib import Path as PathLib

router = APIRouter()

# Base directories for image storage
PICS_DIR = "/app/imgs/pics"
THUMBNAILS_DIR = "/app/imgs/thumbnails"

@router.get("/pics/{filename}")
async def get_picture(filename: str = Path(..., description="Nombre del archivo de imagen")):
    """
    Obtener una imagen en formato binario.
    
    Args:
        filename: Nombre del archivo de imagen
        
    Returns:
        Datos binarios de la imagen con el content-type apropiado
    """
    file_path = os.path.join(PICS_DIR, filename)
    
    # Validate file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    
    # Validate it's actually a file (not a directory)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=400, detail="Ruta inválida")
    
    # Get file extension to determine content type
    ext = PathLib(filename).suffix.lower()
    content_type_map = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    
    content_type = content_type_map.get(ext, 'image/jpeg')
    
    # Read file and return binary data
    try:
        with open(file_path, 'rb') as f:
            image_data = f.read()
        
        return Response(
            content=image_data,
            media_type=content_type,
            headers={
                'Cache-Control': 'public, max-age=31536000',  # Cache for 1 year
                'Content-Disposition': f'inline; filename="{filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer la imagen: {str(e)}")


@router.get("/thumbnails/{filename}")
async def get_thumbnail(filename: str = Path(..., description="Nombre del archivo de thumbnail")):
    """
    Obtener un thumbnail en formato binario.
    
    Args:
        filename: Nombre del archivo de thumbnail (debe incluir 'thumb_' prefix)
        
    Returns:
        Datos binarios del thumbnail con el content-type apropiado
    """
    file_path = os.path.join(THUMBNAILS_DIR, filename)
    
    # Validate file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Thumbnail no encontrado")
    
    # Validate it's actually a file (not a directory)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=400, detail="Ruta inválida")
    
    # Get file extension to determine content type
    ext = PathLib(filename).suffix.lower()
    content_type_map = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    
    content_type = content_type_map.get(ext, 'image/jpeg')
    
    # Read file and return binary data
    try:
        with open(file_path, 'rb') as f:
            image_data = f.read()
        
        return Response(
            content=image_data,
            media_type=content_type,
            headers={
                'Cache-Control': 'public, max-age=31536000',  # Cache for 1 year
                'Content-Disposition': f'inline; filename="{filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer el thumbnail: {str(e)}")


@router.get("/list-pics")
async def list_pictures():
    """
    Listar todas las imágenes disponibles (útil para desarrollo/debug).
    
    Returns:
        Lista de nombres de archivos de imágenes
    """
    try:
        if not os.path.exists(PICS_DIR):
            return {"images": []}
        
        files = [f for f in os.listdir(PICS_DIR) if os.path.isfile(os.path.join(PICS_DIR, f))]
        return {"images": files, "count": len(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar imágenes: {str(e)}")


@router.get("/list-thumbnails")
async def list_thumbnails():
    """
    Listar todos los thumbnails disponibles (útil para desarrollo/debug).
    
    Returns:
        Lista de nombres de archivos de thumbnails
    """
    try:
        if not os.path.exists(THUMBNAILS_DIR):
            return {"thumbnails": []}
        
        files = [f for f in os.listdir(THUMBNAILS_DIR) if os.path.isfile(os.path.join(THUMBNAILS_DIR, f))]
        return {"thumbnails": files, "count": len(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar thumbnails: {str(e)}")
