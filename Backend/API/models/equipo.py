from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID

class EquipoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del equipo")

class EquipoCreate(EquipoBase):
    liga_id: UUID = Field(..., description="ID de la liga")
    usuario_id: UUID = Field(..., description="ID del usuario propietario")
    thumbnail: Optional[str] = Field(None, description="URL del thumbnail del equipo")
    
class EquipoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre del equipo")
    thumbnail: Optional[str] = Field(None, description="URL del thumbnail del equipo")
    liga_id: Optional[UUID] = Field(None, description="Nuevo ID de la liga a la que se moverá el equipo")

class EquipoInDB(EquipoBase):
    id: UUID = Field(..., description="ID único del equipo")
    liga_id: UUID = Field(..., description="ID de la liga")
    usuario_id: UUID = Field(..., description="ID del usuario propietario")
    creado_en: datetime = Field(..., description="Fecha de creación")
    actualizado_en: datetime = Field(..., description="Fecha de actualización")
    thumbnail: Optional[str] = Field(None, description="URL del thumbnail del equipo")
    
    class Config:
        from_attributes = True

class Equipo(EquipoInDB):
    pass

class EquipoResponse(EquipoInDB):
    """Modelo de respuesta para equipos"""
    pass


class EquipoConMedia(EquipoResponse):
    """Modelo de respuesta para equipos con información de media"""
    media_url: Optional[str] = Field(None, description="URL de media asociada")