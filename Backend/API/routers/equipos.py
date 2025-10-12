from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID, uuid4
from datetime import datetime
from models.equipo import Equipo, EquipoCreate, EquipoUpdate, EquipoResponse

router = APIRouter()

# Simulación de base de datos en memoria
equipos_db = {}

@router.post("/", response_model=EquipoResponse, status_code=status.HTTP_201_CREATED)
async def crear_equipo(equipo: EquipoCreate):
    """Crear un nuevo equipo"""
    
    # Verificar restricciones únicas de la base de datos
    for existing_equipo in equipos_db.values():
        # Un usuario solo puede tener un equipo por liga
        if (existing_equipo.liga_id == equipo.liga_id and 
            existing_equipo.usuario_id == equipo.usuario_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario ya tiene un equipo en esta liga"
            )
        
        # El nombre del equipo debe ser único por liga
        if (existing_equipo.liga_id == equipo.liga_id and 
            existing_equipo.nombre.lower() == equipo.nombre.lower()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un equipo con este nombre en la liga"
            )
    
    # Crear el equipo
    equipo_id = uuid4()
    now = datetime.now()
    nuevo_equipo = Equipo(
        id=equipo_id,
        liga_id=equipo.liga_id,
        usuario_id=equipo.usuario_id,
        nombre=equipo.nombre,
        creado_en=now,
        actualizado_en=now
    )
    
    equipos_db[equipo_id] = nuevo_equipo
    return EquipoResponse.from_orm(nuevo_equipo)

@router.get("/", response_model=List[EquipoResponse])
async def obtener_equipos():
    """Obtener todos los equipos"""
    return [EquipoResponse.from_orm(equipo) for equipo in equipos_db.values()]

@router.get("/{equipo_id}", response_model=EquipoResponse)
async def obtener_equipo(equipo_id: UUID):
    """Obtener un equipo por ID"""
    if equipo_id not in equipos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado"
        )
    return EquipoResponse.from_orm(equipos_db[equipo_id])

@router.put("/{equipo_id}", response_model=EquipoResponse)
async def actualizar_equipo(equipo_id: UUID, equipo_update: EquipoUpdate):
    """Actualizar un equipo"""
    if equipo_id not in equipos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado"
        )
    
    equipo_actual = equipos_db[equipo_id]
    
    # Actualizar solo los campos proporcionados
    update_data = equipo_update.dict(exclude_unset=True)
    
    # Verificar si el nombre ya existe en la liga (si se está actualizando)
    if "nombre" in update_data:
        for eid, existing_equipo in equipos_db.items():
            if (eid != equipo_id and 
                existing_equipo.liga_id == equipo_actual.liga_id and 
                existing_equipo.nombre.lower() == update_data["nombre"].lower()):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un equipo con este nombre en la liga"
                )
    
    for field, value in update_data.items():
        setattr(equipo_actual, field, value)
    
    # Actualizar fecha de modificación
    equipo_actual.actualizado_en = datetime.now()
    
    equipos_db[equipo_id] = equipo_actual
    return EquipoResponse.from_orm(equipo_actual)

@router.delete("/{equipo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_equipo(equipo_id: UUID):
    """Eliminar un equipo"""
    if equipo_id not in equipos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado"
        )
    
    # En un sistema real, aquí también se eliminarían los registros
    # de media asociados debido al CASCADE en la base de datos
    del equipos_db[equipo_id]
    return

@router.get("/liga/{liga_id}", response_model=List[EquipoResponse])
async def obtener_equipos_por_liga(liga_id: UUID):
    """Obtener todos los equipos de una liga específica"""
    equipos_liga = []
    
    for equipo in equipos_db.values():
        if equipo.liga_id == liga_id:
            equipos_liga.append(EquipoResponse.from_orm(equipo))
    
    return equipos_liga

@router.get("/usuario/{usuario_id}", response_model=List[EquipoResponse])
async def obtener_equipos_por_usuario(usuario_id: UUID):
    """Obtener todos los equipos de un usuario específico"""
    equipos_usuario = []
    
    for equipo in equipos_db.values():
        if equipo.usuario_id == usuario_id:
            equipos_usuario.append(EquipoResponse.from_orm(equipo))
    
    return equipos_usuario

@router.get("/liga/{liga_id}/usuario/{usuario_id}", response_model=EquipoResponse)
async def obtener_equipo_por_liga_y_usuario(liga_id: UUID, usuario_id: UUID):
    """Obtener el equipo de un usuario en una liga específica"""
    for equipo in equipos_db.values():
        if equipo.liga_id == liga_id and equipo.usuario_id == usuario_id:
            return EquipoResponse.from_orm(equipo)
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="El usuario no tiene un equipo en esta liga"
    )