"""
Business logic service for Usuario operations with separation of concerns
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
from uuid import UUID
import os
import re

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from jose import jwt, JWTError

from models.usuario import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
    RolUsuario,
    EstadoUsuario,
)
from models.database_models import UsuarioDB, RolUsuarioEnum, EstadoUsuarioEnum
from repositories.usuario_repository import usuario_repository
from services.auth_service import auth_service, SECRET_KEY, ALGORITHM
from services.email_service import send_unlock_email
from services.security_service import security_service


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
    
    def crear_usuario(self, db: Session, usuario: UsuarioCreate) -> UsuarioResponse:
        """Create a new user"""
        # Validate unique email
        if usuario_repository.exists_by_correo(db, usuario.correo):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está registrado"
            )
        
        # Validate unique alias if provided
        if usuario.alias and usuario_repository.exists_by_alias(db, usuario.alias):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El alias ya está en uso"
            )

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
        
        nuevo_usuario = usuario_repository.create(db, UsuarioDB(**user_data))
        return _convert_usuario_to_response(nuevo_usuario)

    def listar_usuarios(self, db: Session, skip: int = 0, limit: int = 100) -> List[UsuarioResponse]:
        """List active users with pagination"""
        usuarios = usuario_repository.get_activos(db, skip, limit)
        return [_convert_usuario_to_response(u) for u in usuarios]

    def obtener_usuario(self, db: Session, usuario_id: UUID) -> UsuarioResponse:
        """Get user by ID"""
        usuario = usuario_repository.get(db, usuario_id)
        if not usuario or usuario.estado == EstadoUsuarioEnum.eliminada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {usuario_id} no encontrado",
            )
        return _convert_usuario_to_response(usuario)

    def actualizar_usuario(self, db: Session, usuario_id: UUID, updates: UsuarioUpdate, requester_id: UUID) -> UsuarioResponse:
        usuario_db = db.query(UsuarioDB).filter(
            UsuarioDB.id == usuario_id,
            UsuarioDB.estado != EstadoUsuarioEnum.eliminada,
        ).first()
        if not usuario_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

        if requester_id != usuario_db.id:
            requester_db = db.query(UsuarioDB).filter(UsuarioDB.id == requester_id).first()
            if not requester_db:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no autorizado")
            requester_rol = getattr(requester_db.rol, "value", requester_db.rol)
            if str(requester_rol) != "administrador":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para actualizar este usuario")

        data = updates.model_dump(exclude_unset=True)
        if "correo" in data and data["correo"] and data["correo"] != usuario_db.correo:
            exists = db.query(UsuarioDB).filter(UsuarioDB.correo == data["correo"]).first()
            if exists:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo electrónico ya está registrado")
            usuario_db.correo = data["correo"]

        if "nombre" in data and data["nombre"] is not None:
            usuario_db.nombre = data["nombre"]
        if "alias" in data:
            usuario_db.alias = data["alias"] or ""
        if "idioma" in data and data["idioma"] is not None:
            usuario_db.idioma = data["idioma"]
        if "imagen_perfil_url" in data and data["imagen_perfil_url"] is not None:
            usuario_db.imagen_perfil_url = data["imagen_perfil_url"]

        db.commit()
        db.refresh(usuario_db)
        return _convert_usuario_to_response(usuario_db)

    # ----- Unlock flow -----
    def solicitar_desbloqueo(self, db: Session, correo: str) -> Dict[str, Any]:
        usuario = db.query(UsuarioDB).filter(UsuarioDB.correo == correo).first()
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

    def confirmar_desbloqueo(self, db: Session, token: str) -> Dict[str, Any]:
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

        usuario = db.query(UsuarioDB).filter(UsuarioDB.id == user_uuid).first()
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

        usuario.estado = EstadoUsuarioEnum.activa
        usuario.failed_attempts = 0
        db.commit()
        db.refresh(usuario)
        return {"ok": True, "message": "Tu cuenta ha sido desbloqueada. Ya puedes iniciar sesión."}

    def _is_strong_password(self, pwd: str) -> bool:
        if not isinstance(pwd, str):
            return False
        if not re.fullmatch(r"[A-Za-z0-9]{8,12}", pwd or ""):
            return False
        if not re.search(r"[a-z]", pwd):
            return False
        if not re.search(r"[A-Z]", pwd):
            return False
        return True

    def establecer_contrasena(self, db: Session, token: str, new_password: str) -> Dict[str, Any]:
        if not self._is_strong_password(new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Contraseña inválida. Debe ser alfanumérica de 8–12 caracteres, con al menos una minúscula y una mayúscula."
                ),
            )

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

        usuario = db.query(UsuarioDB).filter(UsuarioDB.id == user_uuid).first()
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

        hashed = auth_service.hash_password(new_password)
        usuario.contrasena_hash = hashed
        usuario.estado = EstadoUsuarioEnum.activa
        usuario.failed_attempts = 0
        db.commit()
        db.refresh(usuario)
        return {"ok": True, "message": "Contraseña actualizada correctamente. Ya puedes iniciar sesión."}


usuario_service = UsuarioService()
