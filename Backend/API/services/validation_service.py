"""
Central validation service coordinator

This service acts as a coordinator for all model-specific validators,
providing a unified interface while delegating to specialized validators.
"""
from typing import Optional
from uuid import UUID

from validators import (
    usuario_validator, temporada_validator, liga_validator, 
    jugador_validator, equipo_nfl_validator, equipo_fantasy_validator,
    media_validator
)
from exceptions.business_exceptions import NotFoundError, ValidationError, ConflictError



class ValidationService:
    """Central validation service that coordinates model-specific validators"""
    
    # Usuario validations
    @staticmethod
    def validate_usuario_exists(usuario_id: UUID):
        """Validate that a user exists"""
        return usuario_validator.validate_exists(usuario_id)
    
    @staticmethod
    def validate_usuario_email(email: str, exclude_id: Optional[UUID] = None):
        """Validate user email format and uniqueness"""
        usuario_validator.validate_email_format(email)
        usuario_validator.validate_email_unique(email, exclude_id)
    
    @staticmethod
    def validate_usuario_password(password: str):
        """Validate user password strength"""
        usuario_validator.validate_password_strength(password)
    
    # Temporada validations
    @staticmethod 
    def validate_temporada_exists(temporada_id: UUID):
        """Validate that a season exists"""
        return temporada_validator.validate_exists(temporada_id)
    
    @staticmethod
    def validate_temporada_dates(fecha_inicio, fecha_fin, exclude_id: Optional[UUID] = None):
        """Validate season dates"""
        temporada_validator.validate_date_range(fecha_inicio, fecha_fin)
        temporada_validator.validate_season_dates_not_overlap(fecha_inicio, fecha_fin, exclude_id)
    
    # Liga validations
    @staticmethod
    def validate_liga_exists(liga_id: UUID):
        """Validate that a league exists"""
        return liga_validator.validate_exists(liga_id)
    
    @staticmethod
    def validate_liga_nombre_unique(nombre: str, exclude_id: Optional[UUID] = None):
        """Validate that league name is unique"""
        liga_validator.validate_nombre_unique(nombre, exclude_id)
    
    @staticmethod
    def validate_liga_editable(liga):
        """Validate that a league can be edited"""
        liga_validator.validate_liga_editable(liga)
    
    @staticmethod
    def validate_liga_has_cupos(liga_id: UUID):
        """Validate that a league has available spots"""
        liga_validator.validate_liga_has_cupos(liga_id)
    
    @staticmethod
    def validate_usuario_not_in_liga(liga_id: UUID, usuario_id: UUID):
        """Validate that a user is not already in the league"""
        liga_validator.validate_usuario_not_in_liga(liga_id, usuario_id)
    
    @staticmethod
    def validate_alias_unique_in_liga(liga_id: UUID, alias: str, exclude_usuario_id: Optional[UUID] = None):
        """Validate that an alias is unique within a league"""
        liga_validator.validate_alias_unique_in_liga(liga_id, alias, exclude_usuario_id)
    
    # Jugador validations
    @staticmethod
    def validate_jugador_exists(jugador_id: UUID):
        """Validate that a player exists"""
        return jugador_validator.validate_exists(jugador_id)
    
    @staticmethod
    def validate_jugador_email(email: str, exclude_id: Optional[UUID] = None):
        """Validate player email"""
        jugador_validator.validate_email_format(email)
        jugador_validator.validate_email_unique(email, exclude_id)
    
    # Equipo NFL validations
    @staticmethod
    def validate_equipo_nfl_exists(equipo_id: UUID):
        """Validate that NFL team exists"""
        return equipo_nfl_validator.validate_exists(equipo_id)
    
    # Equipo Fantasy validations
    @staticmethod
    def validate_equipo_fantasy_exists(equipo_id: UUID):
        """Validate that fantasy team exists"""
        return equipo_fantasy_validator.validate_exists(equipo_id)
    
    # Media validations
    @staticmethod
    def validate_media_exists(media_id: UUID):
        """Validate that media exists"""
        return media_validator.validate_exists(media_id)
    
    # Helper methods
    @staticmethod
    def get_liga_current_members_count(liga_id: UUID) -> int:
        """Get the current number of members in a league"""
        return liga_validator.get_liga_current_members_count(liga_id)
    
    # Utility validation methods
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Check if email format is valid"""
        try:
            usuario_validator.validate_email_format(email)
            return True
        except ValidationError:
            return False
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL format is valid"""
        try:
            media_validator.validate_url_format(url)
            return True
        except ValidationError:
            return False


# Create service instance
validation_service = ValidationService()