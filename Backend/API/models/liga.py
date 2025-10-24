from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any, List
from enum import Enum


class EstadoLiga(str, Enum):
    PRE_DRAFT = "Pre_draft"
    DRAFT = "Draft"


class RolMembresia(str, Enum):
    COMISIONADO = "Comisionado"
    MANAGER = "Manager"


class LigaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre de la liga")
    descripcion: Optional[str] = Field(None, description="Descripción de la liga")
    contrasena: str = Field(..., min_length=4, description="Contraseña de la liga")
    equipos_max: int = Field(..., description="Número máximo de equipos")
    temporada_id: UUID = Field(..., description="ID de la temporada")
    comisionado_id: UUID = Field(..., description="ID del comisionado")
    
    # Configuraciones opcionales
    playoffs_equipos: Optional[int] = Field(4, description="Equipos en playoffs")
    puntajes_decimales: Optional[bool] = Field(True, description="Permitir puntajes decimales")
    trade_deadline_activa: Optional[bool] = Field(False, description="Trade deadline activo")
    limite_cambios_temp: Optional[int] = Field(None, description="Límite de cambios por temporada")
    limite_agentes_temp: Optional[int] = Field(None, description="Límite de agentes por temporada")
    formato_posiciones: Optional[Dict[str, int]] = Field(None, description="Formato de posiciones")
    puntos_config: Optional[Dict[str, Any]] = Field(None, description="Configuración de puntos")

    @validator('equipos_max')
    def validar_equipos_max(cls, v):
        if v not in [4, 6, 8, 10, 12, 14, 16, 18, 20]:
            raise ValueError('Equipos máximos debe ser uno de: 4, 6, 8, 10, 12, 14, 16, 18, 20')
        return v

    @validator('playoffs_equipos')
    def validar_playoffs_equipos(cls, v):
        if v and v not in [4, 6]:
            raise ValueError('Equipos en playoffs debe ser 4 o 6')
        return v


class LigaCreate(LigaBase):
    pass


class LigaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    equipos_max: Optional[int] = None
    playoffs_equipos: Optional[int] = None
    puntajes_decimales: Optional[bool] = None
    trade_deadline_activa: Optional[bool] = None
    limite_cambios_temp: Optional[int] = None
    limite_agentes_temp: Optional[int] = None
    formato_posiciones: Optional[Dict[str, int]] = None
    puntos_config: Optional[Dict[str, Any]] = None


class LigaInDB(BaseModel):
    id: UUID = Field(..., description="ID único de la liga")
    nombre: str = Field(..., description="Nombre de la liga")
    descripcion: Optional[str] = Field(None, description="Descripción de la liga")
    equipos_max: int = Field(..., description="Número máximo de equipos")
    estado: EstadoLiga = Field(..., description="Estado de la liga")
    temporada_id: UUID = Field(..., description="ID de la temporada")
    comisionado_id: UUID = Field(..., description="ID del comisionado")
    playoffs_equipos: int = Field(..., description="Equipos en playoffs")
    puntajes_decimales: bool = Field(..., description="Puntajes decimales")
    trade_deadline_activa: bool = Field(..., description="Trade deadline activo")
    limite_cambios_temp: Optional[int] = Field(None, description="Límite cambios temporada")
    limite_agentes_temp: Optional[int] = Field(None, description="Límite agentes temporada")
    formato_posiciones: Optional[Dict[str, int]] = Field(None, description="Formato de posiciones")
    puntos_config: Optional[Dict[str, Any]] = Field(None, description="Configuración de puntos")
    creado_en: datetime = Field(..., description="Fecha de creación")
    actualizado_en: datetime = Field(..., description="Fecha de actualización")

    class Config:
        from_attributes = True


class LigaResponse(LigaInDB):
    pass


class LigaMiembroBase(BaseModel):
    alias: str = Field(..., min_length=1, max_length=50, description="Alias del miembro")
    rol: Optional[RolMembresia] = Field(RolMembresia.MANAGER, description="Rol del miembro")


class LigaMiembroCreate(LigaMiembroBase):
    liga_id: UUID = Field(..., description="ID de la liga")
    usuario_id: UUID = Field(..., description="ID del usuario")


class LigaMiembroInDB(LigaMiembroBase):
    liga_id: UUID = Field(..., description="ID de la liga")
    usuario_id: UUID = Field(..., description="ID del usuario")
    creado_en: datetime = Field(..., description="Fecha de incorporación")

    class Config:
        from_attributes = True


class LigaMiembroResponse(LigaMiembroInDB):
    pass


class LigaConMiembros(LigaResponse):
    miembros: List[LigaMiembroResponse] = Field(default=[], description="Miembros de la liga")
