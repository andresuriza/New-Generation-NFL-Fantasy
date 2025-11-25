"""
API Router for Jugadores (Players) endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
import os
import json
from datetime import datetime

from models.jugador import (
    JugadorResponse, JugadorCreate, JugadorUpdate, JugadorConEquipo, 
    JugadorFilter, JugadorBulkRequest, JugadorBulkResult,
    NoticiaJugadorCreate, NoticiaJugadorResponse, NoticiaJugadorConAutor
)
from models.database_models import PosicionJugadorEnum
from services.jugador_service import jugador_service
from services.noticia_jugador_service import noticia_jugador_service
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
    uploaded_file_path = None
    try:
        # Directorio en Docker
        uploads_dir = "/app/processed_uploads"
        os.makedirs(uploads_dir, exist_ok=True)

        base_name = request.filename or 'jugadores'
        base_name = os.path.splitext(base_name)[0]
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        temp_filename = f"{timestamp}_processing_{base_name}.json"
        temp_path = os.path.join(uploads_dir, temp_filename)

        print(f"Guardando a: {temp_path}")
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(request.dict(), f, ensure_ascii=False, indent=2, default=str)
        
        uploaded_file_path = temp_path
        
    except Exception as e:
        print(f"Error guardando archivo: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "No se pudo guardar el archivo entrante", "error": str(e)}
        )

    result = jugador_service.crear_jugadores_bulk(db, request.jugadores, request.filename)

    try:
        if uploaded_file_path and os.path.exists(uploaded_file_path):
            status_label = 'success' if getattr(result, 'success', False) else 'error'
            final_filename = f"{timestamp}_{status_label}_{base_name}.json"
            final_path = os.path.join(os.path.dirname(uploaded_file_path), final_filename)
            
            print(f"[DEBUG] Renaming from: {uploaded_file_path}")
            print(f"[DEBUG] Renaming to: {final_path}")
            
            # Overwrite if exists
            if os.path.exists(final_path):
                os.remove(final_path)
            os.replace(uploaded_file_path, final_path)
            
            print(f"[DEBUG] File renamed successfully to: {final_path}")

            # If the result object supports a `processed_file` attribute, set it
            if hasattr(result, 'processed_file'):
                try:
                    setattr(result, 'processed_file', final_path)
                except Exception:
                    pass

    except Exception as e:
        print(f"[DEBUG] Error renaming file: {str(e)}")
        import traceback
        traceback.print_exc()
        pass

    # Si la operación no fue exitosa, retornar error 400
    if not getattr(result, 'success', False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Error en la creación masiva de jugadores",
                "created_count": getattr(result, 'created_count', 0),
                "error_count": getattr(result, 'error_count', 0),
                "errors": getattr(result, 'errors', []),
                "processed_file": getattr(result, 'processed_file', None)
            }
        )

    return result

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

# ============================================================================
# NOTICIAS DE JUGADORES (Player News)
# ============================================================================

@router.post("/{jugador_id}/noticias", response_model=NoticiaJugadorResponse, status_code=status.HTTP_201_CREATED)
async def crear_noticia_jugador(
    jugador_id: UUID,
    noticia: NoticiaJugadorCreate,
    db: Session = Depends(get_db),
    # current_user: Any = Depends(get_current_user)  # TODO: Implement authentication
):
    """
    Crear una noticia para un jugador.
    
    Características:
    • El formulario acepta un texto entre 10 y 300 caracteres y un indicador de si la noticia es de lesión
    • La fecha/hora de creación se autogenera al momento de guardar
    • Si la noticia es de lesión, además se requiere un resumen de hasta 30 caracteres y una designación: O, D, Q, P/FP, IR, PUP o SUS
    • Se registra auditoría (autor, fecha/hora, cambios)
    
    Comportamientos alternativos:
    • Si el texto no cumple los límites o falta la designación en una noticia de lesión, se rechaza con mensaje claro
    • Si el jugador no existe o está inactivo, se rechaza con mensaje claro
    
    Información adicional – designaciones de lesión:
    • Fuera (O): no jugarán
    • Dudoso (D): muy poco probable que jueguen (~25%)
    • Cuestionable (Q): probabilidad ~50%, suele definirse el día del partido
    • Probable (P) / Participación Plena (FP): casi seguro que juega (usado en reportes de práctica)
    • Reserva de Lesionados (IR): fuera por periodo extendido según reglas de la liga/NFL
    • Incapaz Físicamente de Jugar (PUP): no habilitado para jugar hasta cumplir requisitos médicos/reglamentarios
    • Suspendido (SUS): no elegible por sanción
    """
    try:
        # TODO: Replace with actual user ID from authentication
        author_id = UUID("d950d818-477e-44d9-b386-17807d818a44")  # Temporary admin ID (Administrator)
        
        return noticia_jugador_service.crear_noticia(db, jugador_id, noticia, author_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Error al crear la noticia del jugador",
                "error": str(e)
            }
        )

@router.get("/{jugador_id}/noticias", response_model=List[NoticiaJugadorResponse])
async def obtener_noticias_jugador(
    jugador_id: UUID,
    skip: int = Query(0, ge=0, description="Elementos a omitir"),
    limit: int = Query(10, ge=1, le=50, description="Límite de elementos"),
    incluir_autor: bool = Query(False, description="Incluir información del autor"),
    db: Session = Depends(get_db)
):
    """Obtener todas las noticias de un jugador"""
    return noticia_jugador_service.obtener_noticias_jugador(
        db, jugador_id, skip, limit, incluir_autor
    )

@router.get("/noticias/lesiones-recientes", response_model=List[NoticiaJugadorConAutor])
async def obtener_noticias_lesiones_recientes(
    days: int = Query(7, ge=1, le=30, description="Días hacia atrás para buscar"),
    skip: int = Query(0, ge=0, description="Elementos a omitir"),
    limit: int = Query(10, ge=1, le=50, description="Límite de elementos"),
    db: Session = Depends(get_db)
):
    """Obtener noticias de lesiones recientes de los últimos N días"""
    return noticia_jugador_service.obtener_noticias_lesiones_recientes(db, days, skip, limit)

@router.get("/noticias/{noticia_id}", response_model=NoticiaJugadorResponse)
async def obtener_noticia_por_id(
    noticia_id: UUID,
    incluir_autor: bool = Query(False, description="Incluir información del autor"),
    db: Session = Depends(get_db)
):
    """Obtener una noticia específica por ID"""
    return noticia_jugador_service.obtener_noticia_por_id(db, noticia_id, incluir_autor)