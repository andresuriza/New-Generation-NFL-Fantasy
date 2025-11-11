"""
Pydantic models for Jugadores (Players) entity
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from models.database_models import PosicionJugadorEnum

# Base model with common fields
class JugadorBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del jugador")
    posicion: PosicionJugadorEnum = Field(..., description="Posición del jugador")
    equipo_id: UUID = Field(..., description="ID del equipo NFL")
    imagen_url: str = Field(..., description="URL de la imagen del jugador")
    thumbnail_url: Optional[str] = Field(None, description="URL del thumbnail del jugador")
    activo: bool = Field(True, description="Si el jugador está activo")

# For creating a new player
class JugadorCreate(BaseModel):
    """
    Modelo para crear un jugador.
    - nombre: requerido
    - posicion: requerido
    - equipo_id: requerido (debe ser un equipo NFL existente)
    - imagen_url: requerido
    - thumbnail_url: opcional, se genera automáticamente si no se proporciona
    - activo: por defecto True
    """
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del jugador")
    posicion: PosicionJugadorEnum = Field(..., description="Posición del jugador")
    equipo_id: UUID = Field(..., description="ID del equipo NFL")
    imagen_url: str = Field(..., description="URL de la imagen del jugador")
    thumbnail_url: Optional[str] = Field(None, description="URL del thumbnail (se genera automáticamente si no se proporciona)")
    activo: bool = Field(default=True, description="Si el jugador está activo")

# For updating a player
class JugadorUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre del jugador")
    posicion: Optional[PosicionJugadorEnum] = Field(None, description="Posición del jugador")
    equipo_id: Optional[UUID] = Field(None, description="ID del equipo NFL")
    imagen_url: Optional[str] = Field(None, description="URL de la imagen del jugador")
    thumbnail_url: Optional[str] = Field(None, description="URL del thumbnail del jugador")
    activo: Optional[bool] = Field(None, description="Si el jugador está activo")

# For API responses
class JugadorResponse(JugadorBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="ID único del jugador")
    creado_en: datetime = Field(..., description="Fecha de creación")

# Extended response with team info
class JugadorConEquipo(JugadorResponse):
    equipo_nfl: Optional["EquipoNFLResponseBasic"] = Field(None, description="Información básica del equipo NFL")

# For listing players with filters
class JugadorFilter(BaseModel):
    posicion: Optional[PosicionJugadorEnum] = Field(None, description="Filtrar por posición")
    equipo_id: Optional[UUID] = Field(None, description="Filtrar por equipo NFL")
    activo: Optional[bool] = Field(None, description="Filtrar por estado activo")
    nombre: Optional[str] = Field(None, description="Buscar por nombre (parcial)")

# Basic NFL team info to avoid circular imports
class EquipoNFLResponseBasic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="ID único del equipo NFL")
    nombre: str = Field(..., description="Nombre del equipo NFL")
    ciudad: str = Field(..., description="Ciudad del equipo NFL")
    thumbnail: Optional[str] = Field(None, description="Thumbnail del equipo NFL")

# Forward reference resolution
JugadorConEquipo.model_rebuild()

# Bulk operations models
class JugadorBulkCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del jugador")
    posicion: PosicionJugadorEnum = Field(..., description="Posición del jugador")
    equipo_nfl: str = Field(..., description="Nombre del equipo NFL")
    imagen: str = Field(..., description="URL de la imagen del jugador")
    id: Optional[str] = Field(None, description="ID personalizado del jugador (opcional)")

class JugadorBulkResult(BaseModel):
    success: bool = Field(..., description="Si la operación fue exitosa")
    created_count: int = Field(..., description="Número de jugadores creados")
    error_count: int = Field(..., description="Número de errores")
    errors: List[str] = Field(default=[], description="Lista de errores encontrados")
    processed_file: Optional[str] = Field(None, description="Nombre del archivo procesado")

class JugadorBulkRequest(BaseModel):
    jugadores: List[JugadorBulkCreate] = Field(..., description="Lista de jugadores a crear")
    filename: Optional[str] = Field(None, description="Nombre del archivo original")