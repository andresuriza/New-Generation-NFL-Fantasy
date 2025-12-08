"""
Usuario validation service
"""
import re
from typing import Optional
from uuid import UUID
from repositories.usuario_repository import UsuarioRepository
from models.database_models import UsuarioDB
from exceptions.business_exceptions import NotFoundError, ValidationError, ConflictError


class UsuarioValidator:
    """Validation service for Usuario model"""
    
    @staticmethod
    def validate_exists(usuario_id: UUID) -> UsuarioDB:
        """Validate that a user exists"""
        usuario = UsuarioRepository().get(usuario_id)
        if not usuario:
            raise NotFoundError("Usuario no encontrado")
        return usuario
    
    @staticmethod
    def validate_email_format(email: str) -> None:
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("Formato de email inválido")
    
    @staticmethod
    def validate_email_unique(email: str, exclude_id: Optional[UUID] = None) -> None:
        """Validate that email is unique"""
        existing_usuario = UsuarioRepository().get_by_correo(email, exclude_id)
        if existing_usuario:
            raise ConflictError("Email ya está registrado")
    
    @staticmethod
    def validate_alias_format(alias: str) -> None:
        """Validate alias format"""
        if not alias or not alias.strip():
            raise ValidationError("El alias es requerido")
        
        if len(alias.strip()) < 3:
            raise ValidationError("El alias debe tener al menos 3 caracteres")
        
        if len(alias.strip()) > 50:
            raise ValidationError("El alias no puede tener más de 50 caracteres")
        
        # Check for valid characters (alphanumeric, underscores, hyphens)
        if not re.match(r'^[a-zA-Z0-9_-]+$', alias.strip()):
            raise ValidationError("El alias solo puede contener letras, números, guiones y guiones bajos")
    
    @staticmethod
    def validate_nombre_format(nombre: str) -> None:
        """Validate nombre format"""
        if not nombre or not nombre.strip():
            raise ValidationError("El nombre es requerido")
        
        if len(nombre.strip()) < 2:
            raise ValidationError("El nombre debe tener al menos 2 caracteres")
        
        if len(nombre.strip()) > 50:
            raise ValidationError("El nombre no puede tener más de 50 caracteres")
    
    @staticmethod
    def validate_password_strength(password: str) -> None:
        """Validate password strength"""
        if not password:
            raise ValidationError("La contraseña es requerida")
        
        if len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres")
        
        if len(password) > 128:
            raise ValidationError("La contraseña no puede tener más de 128 caracteres")
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValidationError("La contraseña debe contener al menos una letra mayúscula")
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            raise ValidationError("La contraseña debe contener al menos una letra minúscula")
        
        # Check for at least one number
        if not re.search(r'\d', password):
            raise ValidationError("La contraseña debe contener al menos un número")
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("La contraseña debe contener al menos un carácter especial")
    
    @staticmethod
    def validate_user_active(usuario: UsuarioDB) -> None:
        """Validate that user is active (not blocked or deleted)"""
        if usuario.estado.value == "bloqueado":
            raise ValidationError("Usuario bloqueado")
        
        if usuario.estado.value == "eliminada":
            raise ValidationError("Usuario eliminado")
    
    @staticmethod
    def validate_user_can_be_modified(usuario: UsuarioDB) -> None:
        """Validate that user can be modified"""
        if usuario.estado.value == "eliminada":
            raise ValidationError("No se puede modificar un usuario eliminado")
    
    @staticmethod
    def validate_alias_unique(alias: str, exclude_id: Optional[UUID] = None) -> None:
        """Validate that alias is unique"""
        if not alias:  # Empty alias is allowed
            return
            
        existing_usuario = UsuarioRepository().get_by_alias(alias, exclude_id)
        if existing_usuario:
            raise ConflictError("El alias ya está en uso")

    @staticmethod
    def validate_user_permission_for_update(requester_id: UUID, target_user_id: UUID) -> None:
        """Validate that a user has permission to update another user"""
        if requester_id != target_user_id:
            requester = UsuarioRepository().get(requester_id)
            if not requester:
                raise ValidationError("Usuario no autorizado")
            
            requester_rol = getattr(requester.rol, "value", requester.rol)
            if str(requester_rol) != "administrador":
                raise ValidationError("No tienes permiso para actualizar este usuario")

    @staticmethod
    def validate_password_strength_for_unlock(password: str) -> None:
        """Validate password strength for unlock flow (specific rules)"""
        if not isinstance(password, str):
            raise ValidationError("Contraseña inválida")
        
        # Alphanumeric 8-12 characters, at least one lowercase and one uppercase
        if not re.fullmatch(r"[A-Za-z0-9]{8,12}", password or ""):
            raise ValidationError("Contraseña debe ser alfanumérica de 8-12 caracteres")
        
        if not re.search(r"[a-z]", password):
            raise ValidationError("Contraseña debe contener al menos una letra minúscula")
        
        if not re.search(r"[A-Z]", password):
            raise ValidationError("Contraseña debe contener al menos una letra mayúscula")

    @staticmethod
    def validate_idioma_supported(idioma: str) -> None:
        """Validate that language is supported"""
        supported_languages = ["Ingles", "Español"]
        if idioma not in supported_languages:
            raise ValidationError(f"Idioma no soportado. Idiomas disponibles: {', '.join(supported_languages)}")


# Create validator instance
usuario_validator = UsuarioValidator()