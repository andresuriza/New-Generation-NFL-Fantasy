"""
Business logic service for Usuario operations with separation of concerns
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
from uuid import UUID
import os
import re

from jose import jwt, JWTError

from models.usuario import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
    RolUsuario,
    EstadoUsuario,
)
from models.database_models import UsuarioDB, RolUsuarioEnum, EstadoUsuarioEnum
from DAL.repositories.usuario_repository import usuario_repository
from services.auth_service import auth_service, SECRET_KEY, ALGORITHM
from services.email_service import send_unlock_email
from services.security_service import security_service
from services.error_handling import handle_db_errors
from validators.usuario_validator import UsuarioValidator
from exceptions.business_exceptions import ConflictError, NotFoundError, ValidationError


def _convert_usuario_to_response(usuario_db: UsuarioDB) -> UsuarioResponse:
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
        creado_en=usuario_db.creado_en,
    )


class UsuarioService:
    """Service for Usuario CRUD operations"""
    
    @handle_db_errors
    def crear_usuario(self,  usuario: UsuarioCreate) -> UsuarioResponse:
        """Create a new user"""
        # Validate all requirements for creating a user
        validator = UsuarioValidator()
        validator.validate_for_create(usuario.correo, usuario.alias)

        # Hash password
        password_hash = auth_service.hash_password(usuario.contrasena)
        
        # Prepare user data
        user_data = usuario.model_dump(exclude={'contrasena', 'confirmar_contrasena'})
        user_data.update({
            'contrasena_hash': password_hash,
            'rol': RolUsuarioEnum(usuario.rol.value),
            'estado': EstadoUsuarioEnum.activa,
            'idioma': usuario.idioma or "Ingles",
            'failed_attempts': 0
        })
        
        nuevo_usuario = usuario_repository.create(user_data)
        return _convert_usuario_to_response(nuevo_usuario)

    @handle_db_errors
    def listar_usuarios(self, skip: int = 0, limit: int = 100) -> List[UsuarioResponse]:
        """List active users with pagination"""
        usuarios = usuario_repository.get_activos(skip, limit)
        return [_convert_usuario_to_response(u) for u in usuarios]

    @handle_db_errors
    def obtener_usuario(self, usuario_id: UUID) -> UsuarioResponse:
        """Get user by ID"""
        usuario = usuario_repository.get(usuario_id)
        if not usuario or usuario.estado == EstadoUsuarioEnum.eliminada:
            raise NotFoundError(f"Usuario con ID {usuario_id} no encontrado")
        return _convert_usuario_to_response(usuario)

    @handle_db_errors
    def actualizar_usuario(self, usuario_id: UUID, updates: UsuarioUpdate, requester_id: UUID) -> UsuarioResponse:
        """Update user information"""
        usuario_db = usuario_repository.get(usuario_id)
        
        if not usuario_db or usuario_db.estado == EstadoUsuarioEnum.eliminada:
            raise NotFoundError("Usuario no encontrado")

        data = updates.model_dump(exclude_unset=True)
        
        # Validate all requirements for updating a user
        validator = UsuarioValidator()
        validator.validate_for_update(
            requester_id, 
            usuario_id, 
            usuario_db,
            new_email=data.get("correo"),
            new_alias=data.get("alias")
        )
        
        # Update user through repository
        usuario_actualizado = usuario_repository.update(usuario_db, data)
        
        return _convert_usuario_to_response(usuario_actualizado)

    # ----- Unlock flow -----
    def solicitar_desbloqueo(self,  correo: str) -> Dict[str, Any]:
        usuario = usuario_repository.get_by_correo(correo)
        if not usuario:
            return {"ok": True, "message": "Si la cuenta existe, se enviará un correo con instrucciones."}

        estado_val = getattr(usuario.estado, "value", usuario.estado)
        if estado_val != "bloqueado":
            return {"ok": True, "message": "Si la cuenta está bloqueada, recibirás instrucciones por correo."}

        expire_minutes = int(os.getenv("UNLOCK_TOKEN_EXPIRE_MINUTES", "60"))
        claims = {
            "sub": str(usuario.id),
            "purpose": "unlock",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=expire_minutes),
        }
        token = jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)
        frontend_url = os.getenv("FRONTEND_PUBLIC_URL", "http://localhost:3000")
        unlock_url = f"{frontend_url}/account/unlock/confirm?token={token}"
        try:
            send_unlock_email(usuario.correo, unlock_url)
        except Exception:
            pass
        return {"ok": True, "message": "Si la cuenta existe y está bloqueada, enviaremos instrucciones a tu correo."}

    def confirmar_desbloqueo(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM],
                options={"require_exp": True, "require_iat": True, "verify_exp": True},
            )
            if payload.get("purpose") != "unlock":
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido para esta operación")
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token de desbloqueo inválido o expirado")

        try:
            user_uuid = UUID(str(user_id))
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido: ID de usuario no es UUID")

        usuario = usuario_repository.get(user_uuid)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

        usuario.estado = EstadoUsuarioEnum.activa
        usuario.failed_attempts = 0
        usuario_repository.update(usuario.id, {"estado": usuario.estado, "failed_attempts": usuario.failed_attempts})
        return {"ok": True, "message": "Tu cuenta ha sido desbloqueada. Ya puedes iniciar sesión."}

    def establecer_contrasena(self, token: str, new_password: str) -> Dict[str, Any]:
        # Validate password strength
        validator = UsuarioValidator()
        validator.validate_password_strength_for_unlock(new_password)

        try:
            data = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM],
                options={"require_exp": True, "require_iat": True, "verify_exp": True},
            )
            if data.get("purpose") != "unlock":
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido para esta operación")
            user_id = data.get("sub")
            if not user_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token de desbloqueo inválido o expirado")

        try:
            user_uuid = UUID(str(user_id))
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido: ID de usuario no es UUID")

        usuario = usuario_repository.get(user_uuid)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

        hashed = auth_service.hash_password(new_password)
        usuario.contrasena_hash = hashed
        usuario.estado = EstadoUsuarioEnum.activa
        usuario.failed_attempts = 0
        usuario_repository.update(usuario.id, {"contrasena_hash": usuario.contrasena_hash, "estado": usuario.estado, "failed_attempts": usuario.failed_attempts})
        return {"ok": True, "message": "Contraseña actualizada correctamente. Ya puedes iniciar sesión."}


# Create a singleton instance
usuario_service = UsuarioService()
