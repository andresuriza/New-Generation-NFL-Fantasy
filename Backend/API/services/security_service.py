"""
Security utilities for password hashing and verification
"""
import bcrypt
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
   
        import re
        
        if len(password) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        
        if len(password) > 12:
            raise ValueError("La contraseña no puede tener más de 12 caracteres")
        
        # Must contain at least one lowercase letter
        if not re.search(r'[a-z]', password):
            raise ValueError("La contraseña debe contener al menos una letra minúscula")
        
        # Must contain at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula")
        
        # Must contain at least one digit
        if not re.search(r'[0-9]', password):
            raise ValueError("La contraseña debe contener al menos un número")
        
        # Must be alphanumeric only (no special characters)
        if not re.match(r'^[a-zA-Z0-9]+$', password):
            raise ValueError("La contraseña debe ser alfanumérica (solo letras y números)")

security_service = SecurityService()