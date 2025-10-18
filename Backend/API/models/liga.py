from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class LigaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre de la liga")


class LigaInDB(LigaBase):
    id: UUID = Field(..., description="ID único de la liga")
    creado_en: datetime = Field(..., description="Fecha de creación")
    actualizado_en: datetime = Field(..., description="Fecha de actualización")

    class Config:
        from_attributes = True


class LigaResponse(LigaInDB):
    pass
