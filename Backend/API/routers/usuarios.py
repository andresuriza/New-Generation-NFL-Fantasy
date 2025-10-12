from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from models.usuario import (
    UsuarioCreate, 
    UsuarioUpdate, 
    UsuarioResponse, 
    UsuarioLogin,
    RolUsuario, 
    EstadoUsuario,
    LoginResponse
)
from models.database_models import UsuarioDB, RolUsuarioEnum, EstadoUsuarioEnum
from database import get_db
from services.auth_service import auth_service

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
async def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """Crear un nuevo usuario"""
    
    # Verificar si el correo ya existe
    existing_usuario = db.query(UsuarioDB).filter(UsuarioDB.correo == usuario.correo).first()
    if existing_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado"
        )
    
    # Crear hash de la contraseña
    password_hash = auth_service.hash_password(usuario.contrasena)
    
    # Crear nuevo usuario en la base de datos
    nuevo_usuario_db = UsuarioDB(
        nombre=usuario.nombre,
        alias=usuario.alias,
        correo=usuario.correo,
        contrasena_hash=password_hash,
        rol=RolUsuarioEnum(usuario.rol.value),
        estado=EstadoUsuarioEnum.activa,
        idioma=usuario.idioma or "Ingles",
        imagen_perfil_url=usuario.imagen_perfil_url,
        failed_attempts=0
    )
    
    # Guardar en la base de datos
    db.add(nuevo_usuario_db)
    db.commit()
    db.refresh(nuevo_usuario_db)
    
    return convert_usuario_to_response(nuevo_usuario_db)

@router.get("/", response_model=List[UsuarioResponse])
async def listar_usuarios(db: Session = Depends(get_db)):
    """Obtener lista de todos los usuarios activos"""
    usuarios = db.query(UsuarioDB).filter(UsuarioDB.estado != EstadoUsuarioEnum.eliminada).all()
    return [convert_usuario_to_response(usuario) for usuario in usuarios]

@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Obtener un usuario específico por ID"""
    usuario = db.query(UsuarioDB).filter(
        UsuarioDB.id == usuario_id,
        UsuarioDB.estado != EstadoUsuarioEnum.eliminada
    ).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    
    return convert_usuario_to_response(usuario)

@router.post("/login", response_model=LoginResponse)
async def login_usuario(credenciales: UsuarioLogin, request: Request, db: Session = Depends(get_db)):
    """
    Autenticación de usuario con las siguientes funcionalidades:
    - Bloqueo automático después de 5 intentos fallidos
    - Sesión global de 12 horas de inactividad
    - Redirección automática al perfil
    - Mensajes de error genéricos por seguridad
    """
    # Autenticar usuario usando el servicio de autenticación
    resultado_login = auth_service.login_user(db, credenciales.correo, credenciales.contrasena)

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
    return LoginResponse(
        access_token=resultado_login["access_token"],
        refresh_token=resultado_login["refresh_token"],
        token_type="bearer",
        usuario=resultado_login["usuario"],
        expires_in=43200,  # 12 horas en segundos
        redirect_to="/player/profile"  # URL de redirección alineada con el frontend
    )
