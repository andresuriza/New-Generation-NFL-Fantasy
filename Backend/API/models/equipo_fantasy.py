"""
Pydantic models for Equipos Fantasy (Fantasy Teams) entity
"""
from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional
from uuid import UUID
from datetime import datetime
import re

# Base model with common fields
class EquipoFantasyBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del equipo fantasy")
    liga_id: UUID = Field(..., description="ID de la liga")
    usuario_id: UUID = Field(..., description="ID del usuario manager")
    imagen_url: Optional[str] = Field(None, description="URL de la imagen del equipo")
    thumbnail_url: Optional[str] = Field(None, description="URL del thumbnail del equipo")

    @validator('imagen_url')
    def validate_imagen_url(cls, v):
        if v is not None and v.strip():
            # Validate image format (JPEG or PNG)
            if not re.match(r'.*\.(jpg|jpeg|png)(\?.*)?$', v, re.IGNORECASE):
                raise ValueError('La imagen debe ser formato JPEG o PNG')
        return v

# For creating a new fantasy team
class EquipoFantasyCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del equipo fantasy")
    liga_id: UUID = Field(..., description="ID de la liga")
    imagen_url: Optional[str] = Field(None, description="URL de la imagen del equipo")

    @validator('imagen_url')
    def validate_imagen_url(cls, v):
        if v is not None and v.strip():
            # Validate image format (JPEG or PNG)
            if not re.match(r'.*\.(jpg|jpeg|png)(\?.*)?$', v, re.IGNORECASE):
                raise ValueError('La imagen debe ser formato JPEG o PNG')
        return v

# For updating a fantasy team
class EquipoFantasyUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre del equipo fantasy")
    imagen_url: Optional[str] = Field(None, description="URL de la imagen del equipo")

    @validator('imagen_url')
    def validate_imagen_url(cls, v):
        if v is not None and v.strip():
            # Validate image format (JPEG or PNG)
            if not re.match(r'.*\.(jpg|jpeg|png)(\?.*)?$', v, re.IGNORECASE):
                raise ValueError('La imagen debe ser formato JPEG o PNG')
        return v

# For API responses
class EquipoFantasyResponse(EquipoFantasyBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="ID único del equipo fantasy")
    creado_en: datetime = Field(..., description="Fecha de creación")
    actualizado_en: datetime = Field(..., description="Fecha de última actualización")

# Extended response with related data
class EquipoFantasyConRelaciones(EquipoFantasyResponse):
    liga: Optional["LigaResponseBasic"] = Field(None, description="Información básica de la liga")
    usuario: Optional["UsuarioResponseBasic"] = Field(None, description="Información básica del usuario")

# For listing fantasy teams with filters
class EquipoFantasyFilter(BaseModel):
    liga_id: Optional[UUID] = Field(None, description="Filtrar por liga")
    usuario_id: Optional[UUID] = Field(None, description="Filtrar por usuario")
    nombre: Optional[str] = Field(None, description="Buscar por nombre (parcial)")

# Basic related entities to avoid circular imports
class LigaResponseBasic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="ID único de la liga")
    nombre: str = Field(..., description="Nombre de la liga")

class UsuarioResponseBasic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="ID único del usuario")
    nombre: str = Field(..., description="Nombre del usuario")
    alias: str = Field(..., description="Alias del usuario")

# Audit models
class EquipoFantasyAuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="ID único del registro de auditoría")
    equipo_fantasy_id: UUID = Field(..., description="ID del equipo fantasy")
    usuario_id: UUID = Field(..., description="ID del usuario que hizo el cambio")
    accion: str = Field(..., description="Acción realizada")
    campo_modificado: Optional[str] = Field(None, description="Campo que fue modificado")
    valor_anterior: Optional[str] = Field(None, description="Valor anterior del campo")
    valor_nuevo: Optional[str] = Field(None, description="Valor nuevo del campo")
    timestamp_accion: datetime = Field(..., description="Fecha y hora del cambio")
    usuario: Optional[UsuarioResponseBasic] = Field(None, description="Usuario que realizó el cambio")

# Forward reference resolution
EquipoFantasyConRelaciones.model_rebuild()