"""
Security utilities for password hashing and verification
"""
import bcrypt
from fastapi import HTTPException, status

class SecurityService:
    """Service for handling security-related operations"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def validate_password_strength(password: str) -> None:
        """Validate password meets security requirements"""
        if len(password) < 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña debe tener al menos 4 caracteres"
            )

security_service = SecurityService()