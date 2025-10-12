from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum
import re

class RolUsuario(str, Enum):
    MANAGER = "manager"
    ADMINISTRADOR = "administrador"

class EstadoUsuario(str, Enum):
    ACTIVA = "activa"
    BLOQUEADO = "bloqueado"
    ELIMINADA = "eliminada"

class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50, description="Nombre del usuario")
    alias: str = Field(..., min_length=1, max_length=50, description="Alias del usuario")
    correo: EmailStr = Field(..., description="Correo electrónico del usuario (máx 50)")
    idioma: str = Field(default="Ingles", max_length=10, description="Idioma preferido")
    imagen_perfil_url: str = Field(default="/img/perfil/default.png", description="URL de la imagen de perfil")

    @validator("correo")
    def correo_longitud_maxima(cls, v: EmailStr):
        if len(str(v)) > 50:
            raise ValueError("El correo no puede exceder 50 caracteres")
        return v

class UsuarioCreate(UsuarioBase):
    contrasena: str = Field(..., min_length=8, max_length=12, description="Contraseña (8–12, alfanumérica, con minúscula y mayúscula)")
    confirmar_contrasena: str = Field(..., min_length=8, max_length=12, description="Confirmación de contraseña")
    rol: RolUsuario = Field(default=RolUsuario.MANAGER, description="Rol del usuario")

    @validator("contrasena")
    def validar_reglas_contrasena(cls, v: str):
        # 8–12 chars, alphanumeric, at least one lowercase and one uppercase
        if len(v) < 8 or len(v) > 12:
            raise ValueError("La contraseña debe tener entre 8 y 12 caracteres")
        if not re.search(r"[a-z]", v):
            raise ValueError("La contraseña debe incluir al menos una letra minúscula")
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe incluir al menos una letra mayúscula")
        if not re.fullmatch(r"[A-Za-z0-9]+", v):
            raise ValueError("La contraseña debe ser alfanumérica (solo letras y números)")
        return v

    @validator("confirmar_contrasena")
    def validar_confirmacion(cls, v: str, values):
        contrasena = values.get("contrasena")
        if contrasena and v != contrasena:
            raise ValueError("La confirmación de contraseña no coincide")
        return v

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=50, description="Nombre del usuario")
    alias: Optional[str] = Field(None, min_length=1, max_length=50, description="Alias del usuario")
    correo: Optional[EmailStr] = Field(None, description="Correo electrónico del usuario")
    idioma: Optional[str] = Field(None, max_length=10, description="Idioma preferido")
    imagen_perfil_url: Optional[str] = Field(None, description="URL de la imagen de perfil")

class UsuarioInDB(UsuarioBase):
    id: UUID = Field(..., description="ID único del usuario")
    contrasena_hash: str = Field(..., description="Hash de la contraseña")
    rol: RolUsuario = Field(..., description="Rol del usuario")
    estado: EstadoUsuario = Field(..., description="Estado del usuario")
    creado_en: datetime = Field(..., description="Fecha de creación")
    
    class Config:
        from_attributes = True

class Usuario(UsuarioInDB):
    pass

class UsuarioResponse(BaseModel):
    """Modelo de respuesta que excluye información sensible"""
    id: UUID
    nombre: str
    alias: str
    correo: EmailStr
    rol: RolUsuario
    estado: EstadoUsuario
    idioma: str
    imagen_perfil_url: str
    creado_en: datetime
    
    class Config:
        from_attributes = True

class UsuarioLogin(BaseModel):
    correo: EmailStr = Field(..., description="Correo electrónico")
    contrasena: str = Field(..., description="Contraseña")

class LoginResponse(BaseModel):
    access_token: str = Field(..., description="Token de acceso JWT")
    refresh_token: str = Field(..., description="Token de actualización")
    token_type: str = Field(default="bearer", description="Tipo de token")
    usuario: UsuarioResponse = Field(..., description="Información del usuario")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")
    redirect_to: str = Field(default="/profile", description="URL de redirección después del login")