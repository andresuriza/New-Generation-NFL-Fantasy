from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

# Configuración JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = 12  # 12 horas según requerimientos

# Configuración de password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración de seguridad HTTP Bearer
security = HTTPBearer()

class AuthService:
    """Servicio de autenticación con JWT y gestión de sesiones"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.max_failed_attempts = 5
    
    def hash_password(self, password: str) -> str:
        """Crear hash de contraseña"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crear token JWT de acceso"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        
        # Agregar información del token
        session_id = str(uuid.uuid4())
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "session_id": session_id,
            "token_type": "access"
        })
        
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        # Registrar sesión activa
        self.active_sessions[session_id] = {
            "user_id": data.get("sub"),
            "token": token,
            "created_at": datetime.utcnow(),
            "expires_at": expire,
            "last_activity": datetime.utcnow()
        }
        
        return token
    
    def create_refresh_token(self, user_id: str) -> str:
        """Crear token de refresh"""
        expire = datetime.utcnow() + timedelta(days=30)  # Refresh token dura 30 días
        
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "token_type": "refresh"
        }
        
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verificar y decodificar token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Verificar tipo de token
            if payload.get("token_type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Tipo de token inválido"
                )
            
            # Verificar si la sesión está activa
            session_id = payload.get("session_id")
            if session_id:
                # La sesión debe existir y estar activa; si no, el token es inválido
                if session_id not in self.active_sessions:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Sesión inválida o cerrada"
                    )

                session = self.active_sessions[session_id]

                # Verificar inactividad ANTES de actualizar la última actividad
                now = datetime.utcnow()
                last_activity = session.get("last_activity") or session.get("created_at")
                if last_activity and (now - last_activity) > timedelta(hours=12):
                    # Expirada por inactividad: invalidar y rechazar
                    self.invalidate_session(session_id)
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Sesión expirada por inactividad"
                    )

                # Todo bien: actualizar última actividad
                session["last_activity"] = now
            
            return payload
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def invalidate_session(self, session_id: str):
        """Invalidar sesión específica"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
    
    def invalidate_all_user_sessions(self, user_id: str):
        """Invalidar todas las sesiones de un usuario"""
        sessions_to_remove = []
        for session_id, session_data in self.active_sessions.items():
            if session_data["user_id"] == user_id:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.active_sessions[session_id]
    
    def increment_failed_attempts(self, usuario_db, db_session: Session) -> int:
        """Incrementar intentos fallidos en la base de datos"""
        # Incrementar contador
        usuario_db.failed_attempts += 1

        # Si alcanza el máximo permitido, bloquear la cuenta
        try:
            from models.database_models import EstadoUsuarioEnum
            if usuario_db.failed_attempts >= self.max_failed_attempts:
                # Cambiar estado a bloqueado (equivalente a 'inactiva' solicitada)
                usuario_db.estado = EstadoUsuarioEnum.bloqueado
        finally:
            # Guardar siempre los cambios
            db_session.commit()

        return usuario_db.failed_attempts
    
    def reset_failed_attempts(self, usuario_db, db_session: Session):
        """Resetear intentos fallidos después de login exitoso"""
        usuario_db.failed_attempts = 0
        db_session.commit()
    
    def get_active_sessions_count(self, user_id: str) -> int:
        """Obtener número de sesiones activas de un usuario"""
        count = 0
        for session_data in self.active_sessions.values():
            if session_data["user_id"] == user_id:
                count += 1
        return count

    def login_user(self, db_session: Session, correo: str, contrasena: str) -> Dict[str, Any]:
        """
        Autenticar usuario con validación de intentos fallidos y bloqueo
        """
        from models.database_models import UsuarioDB, EstadoUsuarioEnum
        from models.usuario import UsuarioResponse, RolUsuario, EstadoUsuario
        
        try:
            # Buscar usuario por correo
            usuario = db_session.query(UsuarioDB).filter(UsuarioDB.correo == correo).first()
            
            if not usuario:
                return {
                    "success": False,
                    "message": "Credenciales inválidas"
                }
            
            # Verificar si la cuenta está activa
            if usuario.estado != EstadoUsuarioEnum.activa:
                return {
                    "success": False,
                    "message": "Cuenta bloqueada"
                }
            
            # Verificar si la cuenta está bloqueada (o debe bloquearse)
            if usuario.failed_attempts >= 5:
                # Asegurar que el estado refleje el bloqueo
                try:
                    from models.database_models import EstadoUsuarioEnum as _EstadoEnum
                    if usuario.estado != _EstadoEnum.bloqueado:
                        usuario.estado = _EstadoEnum.bloqueado
                        db_session.commit()
                except Exception:
                    # Si no se puede actualizar el estado por cualquier razón, continuar devolviendo error
                    pass
                return {
                    "success": False,
                    "message": "Cuenta inactiva por múltiples intentos fallidos"
                }
            
            # Verificar contraseña
            if not self.verify_password(contrasena, usuario.contrasena_hash):
                # Incrementar intentos fallidos
                new_attempts = self.increment_failed_attempts(usuario, db_session)
                
                message = "Credenciales inválidas"
                if new_attempts >= 5:
                    message = "Cuenta inactiva por múltiples intentos fallidos"
                
                return {
                    "success": False,
                    "message": message
                }
            
            # Login exitoso - resetear intentos fallidos
            self.reset_failed_attempts(usuario, db_session)
            
            # Crear tokens
            access_token = self.create_access_token(data={"sub": str(usuario.id)})
            refresh_token = self.create_refresh_token(str(usuario.id))
            
            # Crear modelo de respuesta del usuario (robusto ante enums o strings)
            rol_val = getattr(usuario.rol, "value", usuario.rol)
            estado_val = getattr(usuario.estado, "value", usuario.estado)

            usuario_response = UsuarioResponse(
                id=usuario.id,
                nombre=usuario.nombre,
                alias=usuario.alias,
                correo=usuario.correo,
                rol=RolUsuario(rol_val),
                estado=EstadoUsuario(estado_val),
                idioma=usuario.idioma,
                imagen_perfil_url=usuario.imagen_perfil_url,
                creado_en=usuario.creado_en
            )
            
            return {
                "success": True,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "usuario": usuario_response,
                "message": "Login exitoso"
            }
            
        except Exception as e:
            # En producción, usar logging apropiado
            # logger.error(f"Error en login_user: {str(e)}")
            return {
                "success": False,
                "message": "Error interno del servidor"
            }

# Instancia global del servicio de autenticación
auth_service = AuthService()

# Dependency para obtener usuario actual
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency para obtener el usuario actual desde el token JWT"""
    token = credentials.credentials
    payload = auth_service.verify_token(token)
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    return {"user_id": user_id, "session_id": payload.get("session_id")}

# Modelos de respuesta para autenticación
from pydantic import BaseModel

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_HOURS * 3600  # en segundos
    user_id: str

class LoginResponse(BaseModel):
    user: dict
    tokens: TokenResponse
    message: str
    redirect_url: str = "/profile"
