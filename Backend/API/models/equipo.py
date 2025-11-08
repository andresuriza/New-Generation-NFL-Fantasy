from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID

class EquipoNFLBase(BaseModel):
    """Modelo base para equipos NFL (equipos reales de la NFL)"""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del equipo NFL")
    ciudad: Optional[str] = Field(None, min_length=1, max_length=100, description="Ciudad del equipo NFL")
    thumbnail: Optional[str] = Field(None, description="URL del thumbnail del equipo")

class EquipoNFLCreate(EquipoNFLBase):
    """Modelo para crear un equipo NFL"""
    pass
    
class EquipoNFLUpdate(BaseModel):
    """Modelo para actualizar un equipo NFL"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre del equipo NFL")
    ciudad: Optional[str] = Field(None, min_length=1, max_length=100, description="Ciudad del equipo NFL")
    thumbnail: Optional[str] = Field(None, description="URL del thumbnail del equipo")

class EquipoNFLResponse(EquipoNFLBase):
    """Modelo de respuesta para equipos NFL"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="ID único del equipo NFL")
    creado_en: datetime = Field(..., description="Fecha de creación")
    actualizado_en: datetime = Field(..., description="Fecha de actualización")

class EquipoNFLResponseBasic(BaseModel):
    """Modelo básico de respuesta para equipos NFL (para evitar imports circulares)"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="ID único del equipo NFL")
    nombre: str = Field(..., description="Nombre del equipo NFL")
    ciudad: str = Field(..., description="Ciudad del equipo NFL")

class EquipoNFLConMedia(EquipoNFLResponse):
    """Modelo de respuesta para equipos NFL con información de media"""
    media_url: Optional[str] = Field(None, description="URL de media asociada")