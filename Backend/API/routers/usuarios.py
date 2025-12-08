from fastapi import APIRouter, HTTPException, Depends, status, Request

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from models.usuario import (
    UsuarioCreate, 
    UsuarioUpdate, 
    UsuarioResponse, 
    UsuarioLogin,
    RolUsuario, 
    EstadoUsuario
)
from models.database_models import UsuarioDB, RolUsuarioEnum, EstadoUsuarioEnum
from database import get_db
from services.auth_service import auth_service
from routers.auth import get_current_user, LoginResponse
from services.usuario_service import usuario_service
from exceptions.business_exceptions import ValidationError, ConflictError, NotFoundError
from jose import JWTError
import re

router = APIRouter()

def convert_usuario_to_response(usuario_db: UsuarioDB) -> UsuarioResponse:
    """Convertir modelo de base de datos a modelo de respuesta"""
    rol_val = getattr(usuario_db.rol, "value", usuario_db.rol)
    estado_val = getattr(usuario_db.estado, "value", usuario_db.estado)

    return UsuarioResponse(
        id=usuario_db.id,
        nombre=usuario_db.nombre,
        alias=usuario_db.alias,
        correo=usuario_db.correo,
        rol=RolUsuario(rol_val),
        estado=EstadoUsuario(estado_val),
        idioma=usuario_db.idioma,
        imagen_perfil_url=usuario_db.imagen_perfil_url,
        creado_en=usuario_db.creado_en
    )

@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario: UsuarioCreate):
    """Crear un nuevo usuario"""
    try:
        return usuario_service.crear_usuario(usuario)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

@router.get("/", response_model=List[UsuarioResponse])
async def listar_usuarios():
    """Obtener lista de todos los usuarios activos"""
    return usuario_service.listar_usuarios()

@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def obtener_usuario(usuario_id: UUID):
    """Obtener un usuario específico por ID"""
    try:
        return usuario_service.obtener_usuario(usuario_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)

@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def actualizar_usuario(
    usuario_id: UUID,
    updates: UsuarioUpdate,
    current=Depends(get_current_user),
):
    """Actualizar datos de perfil del usuario.
    Reglas:
    - Requiere autenticación.
    - Un usuario solo puede actualizar su propio perfil, excepto administradores.
    - Campos permitidos: nombre, alias, idioma, imagen_perfil_url, (correo opcional con verificación de unicidad).
    """
    try:
        requester_id = UUID(str(current.get("user_id")))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    
    try:
        return usuario_service.actualizar_usuario(usuario_id, updates, requester_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

@router.post("/login", response_model=LoginResponse)
async def login_usuario(credenciales: UsuarioLogin, request: Request):
    """
    Autenticación de usuario con las siguientes funcionalidades:
    - Bloqueo automático después de 5 intentos fallidos
    - Sesión global de 12 horas de inactividad
    - Redirección automática al perfil
    - Mensajes de error genéricos por seguridad
    """
    # Autenticar usuario usando el servicio de autenticación
    resultado_login = auth_service.login_user(credenciales.correo, credenciales.contrasena)

    if not resultado_login.get("success"):
        # Propagar mensaje específico cuando corresponda
        msg = (resultado_login.get("message") or "Credenciales inválidas").strip()
        code = status.HTTP_401_UNAUTHORIZED
        lower = msg.lower()
        # Si la cuenta está bloqueada/inactiva/no activa, usar 423 Locked
        if any(t in lower for t in ("inactiva", "bloqueada", "no activa")):
            code = status.HTTP_423_LOCKED
        raise HTTPException(status_code=code, detail=msg)

    # Login exitoso, devolver tokens y información del usuario
    from routers.auth import TokenResponse
    
    tokens = TokenResponse(
        access_token=resultado_login["access_token"],
        refresh_token=resultado_login["refresh_token"],
        token_type="bearer",
        expires_in=43200,  # 12 horas en segundos
        user_id=str(resultado_login["usuario"].id)
    )
    
    return LoginResponse(
        user=resultado_login["usuario"].dict(),
        tokens=tokens,
        message=resultado_login["message"],
        redirect_url="/player/profile"
    )


# ====== Desbloqueo de cuenta ======
from pydantic import BaseModel, EmailStr

class UnlockRequest(BaseModel):
    correo: EmailStr

class UnlockConfirm(BaseModel):
    token: str

class UnlockSetPassword(BaseModel):
    token: str
    new_password: str

@router.post("/unlock/request")
async def solicitar_desbloqueo(payload: UnlockRequest):
    return usuario_service.solicitar_desbloqueo(payload.correo)


@router.get("/unlock/confirm")
async def confirmar_desbloqueo(token: str):
    return usuario_service.confirmar_desbloqueo(token)


def _is_strong_password(pwd: str) -> bool:
    """Policy: 8–12 chars, alphanumeric only, at least one lowercase and one uppercase."""
    if not isinstance(pwd, str):
        return False
    # Length and allowed chars only
    if not re.fullmatch(r"[A-Za-z0-9]{8,12}", pwd or ""):
        return False
    # Must include at least one lowercase and one uppercase
    if not re.search(r"[a-z]", pwd):
        return False
    if not re.search(r"[A-Z]", pwd):
        return False
    return True


@router.post("/unlock/set-password")
async def establecer_contrasena(payload: UnlockSetPassword):
    """Permitir establecer una nueva contraseña usando el token de desbloqueo."""
    return usuario_service.establecer_contrasena(payload.token, payload.new_password)
