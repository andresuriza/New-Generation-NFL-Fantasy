from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, Any
from services.auth_service import auth_service, ACCESS_TOKEN_EXPIRE_HOURS

# Configuración de seguridad HTTP Bearer
security = HTTPBearer()

# Modelos de respuesta para autenticación
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

# Dependency para obtener usuario actual
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Dependency para obtener el usuario actual desde el token JWT"""
    token = credentials.credentials
    
    try:
        payload = auth_service.verify_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        return {"user_id": user_id, "session_id": payload.get("session_id")}
    
    except ValueError as e:
        error_msg = str(e)
        
        # Mapear diferentes tipos de errores de autenticación
        if "expirada por inactividad" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sesión expirada por inactividad"
            )
        elif "expirado" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado"
            )
        elif "inválido" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Error de autenticación"
            )