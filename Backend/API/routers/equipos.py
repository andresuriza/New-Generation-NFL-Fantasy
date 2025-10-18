from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from models.equipo import EquipoCreate, EquipoUpdate, EquipoResponse
from models.database_models import EquipoDB
from database import get_db

router = APIRouter()

def to_response(e: EquipoDB) -> EquipoResponse:
    return EquipoResponse.model_validate(e, from_attributes=True)

@router.post("/", response_model=EquipoResponse, status_code=status.HTTP_201_CREATED)
async def crear_equipo(equipo: EquipoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo equipo"""
    # Un usuario solo puede tener un equipo por liga
    exists_user_team = db.query(EquipoDB).filter(
        EquipoDB.liga_id == equipo.liga_id,
        EquipoDB.usuario_id == equipo.usuario_id,
    ).first()
    if exists_user_team:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya tiene un equipo en esta liga")

    # El nombre del equipo debe ser único por liga (case-insensitive)
    exists_name = db.query(EquipoDB).filter(
        EquipoDB.liga_id == equipo.liga_id,
        EquipoDB.nombre.ilike(equipo.nombre)
    ).first()
    if exists_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un equipo con este nombre en la liga")

    nuevo = EquipoDB(
        liga_id=equipo.liga_id,
        usuario_id=equipo.usuario_id,
        nombre=equipo.nombre,
        thumbnail=equipo.thumbnail,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return to_response(nuevo)

@router.get("/", response_model=List[EquipoResponse])
async def obtener_equipos(db: Session = Depends(get_db)):
    items = db.query(EquipoDB).all()
    return [to_response(e) for e in items]

@router.get("/{equipo_id}", response_model=EquipoResponse)
async def obtener_equipo(equipo_id: UUID, db: Session = Depends(get_db)):
    e = db.query(EquipoDB).filter(EquipoDB.id == equipo_id).first()
    if not e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipo no encontrado")
    return to_response(e)

@router.put("/{equipo_id}", response_model=EquipoResponse)
async def actualizar_equipo(equipo_id: UUID, equipo_update: EquipoUpdate, db: Session = Depends(get_db)):
    e = db.query(EquipoDB).filter(EquipoDB.id == equipo_id).first()
    if not e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipo no encontrado")

    data = equipo_update.model_dump(exclude_unset=True)
    # Determine target league (original or new one if provided)
    target_liga_id = data.get("liga_id", e.liga_id)
    target_nombre = data.get("nombre", e.nombre)

    # If moving leagues, ensure user doesn't already have a team in target league
    if target_liga_id != e.liga_id:
        exists_user_team = db.query(EquipoDB).filter(
            EquipoDB.liga_id == target_liga_id,
            EquipoDB.usuario_id == e.usuario_id,
        ).first()
        if exists_user_team:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya tiene un equipo en la liga destino")

    # Validate unique team name within target league (case-insensitive)
    if "nombre" in data or ("liga_id" in data and target_liga_id != e.liga_id):
        conflict = db.query(EquipoDB).filter(
            EquipoDB.id != equipo_id,
            EquipoDB.liga_id == target_liga_id,
            EquipoDB.nombre.ilike(target_nombre),
        ).first()
        if conflict:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un equipo con este nombre en la liga destino")

    for k, v in data.items():
        setattr(e, k, v)

    db.commit()
    db.refresh(e)
    return to_response(e)

@router.delete("/{equipo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_equipo(equipo_id: UUID, db: Session = Depends(get_db)):
    e = db.query(EquipoDB).filter(EquipoDB.id == equipo_id).first()
    if not e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipo no encontrado")
    db.delete(e)
    db.commit()
    return

@router.get("/liga/{liga_id}", response_model=List[EquipoResponse])
async def obtener_equipos_por_liga(liga_id: UUID, db: Session = Depends(get_db)):
    items = db.query(EquipoDB).filter(EquipoDB.liga_id == liga_id).all()
    return [to_response(e) for e in items]

@router.get("/usuario/{usuario_id}", response_model=List[EquipoResponse])
async def obtener_equipos_por_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    items = db.query(EquipoDB).filter(EquipoDB.usuario_id == usuario_id).all()
    return [to_response(e) for e in items]

@router.get("/liga/{liga_id}/usuario/{usuario_id}", response_model=EquipoResponse)
async def obtener_equipo_por_liga_y_usuario(liga_id: UUID, usuario_id: UUID, db: Session = Depends(get_db)):
    e = db.query(EquipoDB).filter(
        EquipoDB.liga_id == liga_id,
        EquipoDB.usuario_id == usuario_id,
    ).first()
    if not e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no tiene un equipo en esta liga")
    return to_response(e)