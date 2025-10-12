from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime
from uuid import UUID

class MediaBase(BaseModel):
    url: str = Field(..., description="URL de la imagen")

class MediaCreate(MediaBase):
    equipo_id: UUID = Field(..., description="ID del equipo asociado")

class MediaUpdate(BaseModel):
    url: Optional[str] = Field(None, description="URL de la imagen")

class MediaInDB(MediaBase):
    equipo_id: UUID = Field(..., description="ID del equipo asociado")
    generado_en: Optional[datetime] = Field(None, description="Fecha de generación")
    creado_en: datetime = Field(..., description="Fecha de creación")
    
    class Config:
        from_attributes = True

class Media(MediaInDB):
    pass

class MediaResponse(MediaInDB):
    """Modelo de respuesta para media"""
    pass