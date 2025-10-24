from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from uuid import UUID
from typing import Optional, List


class TemporadaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre de la temporada")
    semanas: int = Field(..., ge=1, le=17, description="Número de semanas (1-17)")
    fecha_inicio: date = Field(..., description="Fecha de inicio de la temporada")
    fecha_fin: date = Field(..., description="Fecha de fin de la temporada")
    es_actual: Optional[bool] = Field(False, description="Si es la temporada actual")

    @validator('fecha_fin')
    def validar_fechas(cls, v, values):
        if 'fecha_inicio' in values and v <= values['fecha_inicio']:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v


class TemporadaCreate(TemporadaBase):
    pass


class TemporadaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    semanas: Optional[int] = Field(None, ge=1, le=17)
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    es_actual: Optional[bool] = None


class TemporadaInDB(TemporadaBase):
    id: UUID = Field(..., description="ID único de la temporada")
    creado_en: datetime = Field(..., description="Fecha de creación")

    class Config:
        from_attributes = True


class TemporadaResponse(TemporadaInDB):
    pass


class TemporadaSemanaBase(BaseModel):
    numero: int = Field(..., ge=1, description="Número de semana")
    fecha_inicio: date = Field(..., description="Fecha de inicio de la semana")
    fecha_fin: date = Field(..., description="Fecha de fin de la semana")

    @validator('fecha_fin')
    def validar_fechas_semana(cls, v, values):
        if 'fecha_inicio' in values and v <= values['fecha_inicio']:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v


class TemporadaSemanaCreate(TemporadaSemanaBase):
    temporada_id: UUID = Field(..., description="ID de la temporada")


class TemporadaSemanaInDB(TemporadaSemanaBase):
    temporada_id: UUID = Field(..., description="ID de la temporada")

    class Config:
        from_attributes = True


class TemporadaSemanaResponse(TemporadaSemanaInDB):
    pass


class TemporadaConSemanas(TemporadaResponse):
    semanas_detalle: List[TemporadaSemanaResponse] = Field(default=[], description="Detalle de semanas")