"""
Equipo Fantasy validation service
"""
import re
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from repositories.equipo_fantasy_repository import EquipoFantasyRepository
from repositories.liga_repository import LigaRepository
from models.database_models import EquipoFantasyDB, UsuarioDB, LigaDB
from exceptions.business_exceptions import NotFoundError, ValidationError, ConflictError


class EquipoFantasyValidator:
    """Validation service for Equipo Fantasy model"""
    
    @staticmethod
    def validate_exists(equipo_id: UUID) -> EquipoFantasyDB:
        """Validate that a fantasy team exists"""
        equipo = EquipoFantasyRepository().get(equipo_id)
        if not equipo:
            raise NotFoundError("Equipo fantasy no encontrado")
        return equipo
    
    @staticmethod
    def validate_nombre_format(nombre: str) -> None:
        """Validate fantasy team name format"""
        if not nombre or not nombre.strip():
            raise ValidationError("El nombre del equipo fantasy es requerido")
        
        if len(nombre.strip()) < 3:
            raise ValidationError("El nombre del equipo debe tener al menos 3 caracteres")
        
        if len(nombre.strip()) > 100:
            raise ValidationError("El nombre del equipo no puede tener más de 100 caracteres")
        
        # Check for appropriate content (no offensive words, etc.)
        # This could be expanded with a profanity filter
        if re.search(r'\b(fuck|shit|damn|hell|bitch)\b', nombre.lower()):
            raise ValidationError("El nombre del equipo contiene lenguaje inapropiado")
    
    @staticmethod
    def validate_nombre_unique_in_liga( nombre: str, liga_id: UUID, exclude_id: Optional[UUID] = None) -> None:
        """Validate that fantasy team name is unique within the league"""
        existing_team = EquipoFantasyRepository().get_by_liga_and_nombre(liga_id, nombre)
        
        if existing_team and (not exclude_id or existing_team.id != exclude_id):
            raise ConflictError("Ya existe un equipo con ese nombre en la liga")
    
    @staticmethod
    def validate_usuario_exists( usuario_id: UUID) -> UsuarioDB:
        """Validate that user exists and is active"""
        usuario = EquipoFantasyRepository().get_usuario_by_id(usuario_id)
        if not usuario:
            raise NotFoundError("Usuario no encontrado")
        
        if usuario.estado.value != "activa":
            raise ValidationError("El usuario debe estar activo")
        
        return usuario
    
    @staticmethod
    def validate_liga_exists(liga_id: UUID) -> LigaDB:
        """Validate that league exists"""
        liga = LigaRepository().get(liga_id)
        if not liga:
            raise NotFoundError("Liga no encontrada")
        return liga
    
    @staticmethod
    def validate_usuario_in_liga(usuario_id: UUID, liga_id: UUID) -> None:
        """Validate that user is a member of the league"""
        is_miembro = LigaRepository().is_usuario_miembro(usuario_id, liga_id)
        
        
        if not is_miembro:
            raise ValidationError("El usuario debe ser miembro de la liga")
    
    @staticmethod
    def validate_usuario_not_has_team_in_liga(usuario_id: UUID, liga_id: UUID, exclude_id: Optional[UUID] = None) -> None:
        """Validate that user doesn't already have a team in this league"""

        existing_team = EquipoFantasyRepository().get_by_usuario_and_liga(usuario_id, liga_id, exclude_id)
        if existing_team:
            raise ConflictError("El usuario ya tiene un equipo en esta liga")
    
    @staticmethod
    def validate_imagen_url_format(imagen_url: Optional[str]) -> None:
        """Validate image URL format - must be JPEG or PNG"""
        if not imagen_url or not imagen_url.strip():
            return
            
        # Validate format (JPEG or PNG only)
        if not re.match(r'.*\.(jpg|jpeg|png)(\?.*)?$', imagen_url, re.IGNORECASE):
            raise ValidationError("La imagen debe ser formato JPEG o PNG")
    
    @staticmethod
    def validate_descripcion_format(descripcion: Optional[str]) -> None:
        """Validate team description format"""
        if descripcion is not None and descripcion.strip():
            if len(descripcion.strip()) > 500:
                raise ValidationError("La descripción no puede tener más de 500 caracteres")
    
    @staticmethod
    def validate_usuario_owns_team(equipo: EquipoFantasyDB, usuario_id: UUID) -> None:
        """Validate that user owns the fantasy team"""
        if equipo.usuario_id != usuario_id:
            raise ValidationError("Solo el propietario puede modificar el equipo")
    
    @staticmethod
    def validate_liga_allows_changes(liga: LigaDB) -> None:
        """Validate that league allows team modifications"""
        if liga.estado.value != "Pre_draft":
            raise ValidationError("No se pueden modificar equipos después del draft")
    
    @staticmethod
    def validate_equipo_activo(equipo: EquipoFantasyDB) -> None:
        """Validate that fantasy team is active"""
        if not equipo.activo:
            raise ValidationError("El equipo fantasy no está activo")
    
    @staticmethod
    def validate_presupuesto(presupuesto: Optional[int]) -> None:
        """Validate team budget"""
        if presupuesto is not None:
            if presupuesto < 0:
                raise ValidationError("El presupuesto no puede ser negativo")
            
            if presupuesto > 1000:  # Assuming max budget of 1000
                raise ValidationError("El presupuesto no puede exceder 1000")
    
    @staticmethod
    def validate_equipo_can_be_deleted(equipo_id: UUID) -> None:
        """Validate that fantasy team can be deleted"""
        equipo = EquipoFantasyValidator.validate_exists(equipo_id)
        
        # Check if league allows deletions
        liga = LigaRepository().get(equipo.liga_id)
        if liga and liga.estado.value != "Pre_draft":
            raise ValidationError("No se puede eliminar el equipo después del draft")
    
    @staticmethod
    def validate_for_create(nombre: str, liga_id: UUID, usuario_id: UUID, imagen_url: Optional[str] = None) -> None:
        """Validate all requirements for creating a fantasy team"""
        EquipoFantasyValidator.validate_liga_exists(liga_id)
        EquipoFantasyValidator.validate_usuario_exists(usuario_id)
        EquipoFantasyValidator.validate_usuario_not_has_team_in_liga(usuario_id, liga_id)
        EquipoFantasyValidator.validate_nombre_unique_in_liga(nombre, liga_id)
        
        if imagen_url:
            EquipoFantasyValidator.validate_imagen_url_format(imagen_url)
    
    @staticmethod
    def validate_for_update(equipo_id: UUID, usuario_id: UUID, nuevo_nombre: Optional[str] = None,
                          nueva_imagen: Optional[str] = None) -> EquipoFantasyDB:
        """Validate all requirements for updating a fantasy team"""
        equipo = EquipoFantasyValidator.validate_exists(equipo_id)
        EquipoFantasyValidator.validate_usuario_owns_team(equipo, usuario_id)
        
        if nuevo_nombre is not None:
            EquipoFantasyValidator.validate_nombre_unique_in_liga(nuevo_nombre, equipo.liga_id, equipo_id)
        
        if nueva_imagen is not None and nueva_imagen.strip():
            EquipoFantasyValidator.validate_imagen_url_format(nueva_imagen)
        
        return equipo


# Create validator instance
equipo_fantasy_validator = EquipoFantasyValidator()