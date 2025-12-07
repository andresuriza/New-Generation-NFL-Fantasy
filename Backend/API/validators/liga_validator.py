"""
Liga validation service
Validators use repositories to access data - NO direct database access
"""
from typing import Optional
from uuid import UUID

from models.database_models import LigaDB, UsuarioDB, TemporadaDB, RolMembresiaEnum
from exceptions.business_exceptions import NotFoundError, ValidationError, ConflictError
from repositories.liga_repository import liga_repository, liga_miembro_repository
from repositories.usuario_repository import usuario_repository
from repositories.temporada_repository import temporada_repository


class LigaValidator:
    """Validation service for Liga model"""
    
    @staticmethod
    def validate_exists(liga_id: UUID) -> LigaDB:
        """Validate that a league exists"""
        liga = liga_repository.get(liga_id)
        if not liga:
            raise NotFoundError("Liga no encontrada")
        return liga
    
    @staticmethod
    def validate_nombre_format(nombre: str) -> None:
        """Validate league name format"""
        if not nombre or not nombre.strip():
            raise ValidationError("El nombre de la liga es requerido")
        
        if len(nombre.strip()) < 3:
            raise ValidationError("El nombre de la liga debe tener al menos 3 caracteres")
        
        if len(nombre.strip()) > 100:
            raise ValidationError("El nombre de la liga no puede tener más de 100 caracteres")
    
    @staticmethod
    def validate_nombre_unique(nombre: str, exclude_id: Optional[UUID] = None) -> None:
        """Validate that league name is unique"""
        liga = liga_repository.get_by_nombre(nombre)
        
        if liga and (not exclude_id or liga.id != exclude_id):
            raise ConflictError("Ya existe una liga con ese nombre")
    
    @staticmethod
    def validate_descripcion_format(descripcion: Optional[str]) -> None:
        """Validate league description format"""
        if descripcion and len(descripcion.strip()) > 500:
            raise ValidationError("La descripción no puede tener más de 500 caracteres")
    
    @staticmethod
    def validate_equipos_max(equipos_max: int) -> None:
        """Validate maximum number of teams"""
        if equipos_max < 2:
            raise ValidationError("La liga debe permitir al menos 2 equipos")
        
        if equipos_max > 20:
            raise ValidationError("La liga no puede tener más de 20 equipos")
    
    @staticmethod
    def validate_comisionado_exists(comisionado_id: UUID) -> UsuarioDB:
        """Validate that commissioner exists and is active"""
        comisionado = usuario_repository.get(comisionado_id)
        if not comisionado:
            raise NotFoundError("Usuario comisionado no encontrado")
        
        if comisionado.estado.value != "activa":
            raise ValidationError("El comisionado debe ser un usuario activo")
        
        return comisionado
    
    @staticmethod
    def validate_temporada_exists(temporada_id: UUID) -> TemporadaDB:
        """Validate that season exists"""
        temporada = temporada_repository.get(temporada_id)
        if not temporada:
            raise NotFoundError("Temporada no encontrada")
        
        return temporada
    
    @staticmethod
    def validate_liga_editable(liga: LigaDB) -> None:
        """Validate that a league can be edited (only in Pre_draft state)"""
        if liga.estado.value != "Pre_draft":
            raise ValidationError("Solo se pueden modificar ligas en estado Pre_draft")
    
    @staticmethod
    def validate_liga_has_cupos(liga_id: UUID) -> None:
        """Validate that a league has available spots"""
        # Get the league to check equipos_max
        liga = liga_repository.get(liga_id)
        if not liga:
            raise NotFoundError("Liga no encontrada")
        
        # Count current members in the league (excluding comisionado)
        # Only count members with Manager role, as Commissioner doesn't count towards limit
        current_members_count = liga_miembro_repository.count_miembros_by_liga(liga_id)
        
        # Check if league is full (use equipos_max as the limit, comisionado doesn't count)
        if current_members_count >= liga.equipos_max:
            raise ValidationError("La liga está llena")
    
    @staticmethod
    def validate_usuario_not_in_liga(liga_id: UUID, usuario_id: UUID) -> None:
        """Validate that a user is not already in the league"""
        miembro_existente = liga_miembro_repository.get_by_liga_usuario(liga_id, usuario_id)
        
        if miembro_existente:
            raise ConflictError("Ya eres miembro de esta liga")
    
    @staticmethod
    def validate_alias_unique_in_liga(liga_id: UUID, alias: str, exclude_usuario_id: Optional[UUID] = None) -> None:
        """Validate that an alias is unique within a league"""
        miembro = liga_miembro_repository.get_by_liga_alias(liga_id, alias)
        
        if miembro and (not exclude_usuario_id or miembro.usuario_id != exclude_usuario_id):
            raise ConflictError("Ese alias ya está ocupado en esta liga")
    
    @staticmethod
    def validate_codigo_invitacion_format(codigo: str) -> None:
        """Validate invitation code format"""
        if not codigo or not codigo.strip():
            raise ValidationError("El código de invitación es requerido")
        
        if len(codigo.strip()) < 6:
            raise ValidationError("El código de invitación debe tener al menos 6 caracteres")
        
        if len(codigo.strip()) > 20:
            raise ValidationError("El código de invitación no puede tener más de 20 caracteres")
    
    @staticmethod
    def validate_codigo_invitacion_unique(codigo: str, exclude_id: Optional[UUID] = None) -> None:
        """Validate that invitation code is unique"""
        # Note: This would need a new repository method get_by_codigo_invitacion
        # For now, we'll leave this as a placeholder
        # TODO: Add get_by_codigo_invitacion method to liga_repository
        pass
    
    @staticmethod
    def validate_liga_can_be_deleted(liga_id: UUID) -> None:
        """Validate that league can be deleted"""
        # Check if league has any members (including commissioner)
        miembros = liga_miembro_repository.get_miembros_by_liga(liga_id)
        if len(miembros) > 0:
            raise ValidationError("No se puede eliminar la liga porque tiene miembros")
    
    @staticmethod
    def validate_usuario_is_comisionado(liga: LigaDB, usuario_id: UUID) -> None:
        """Validate that user is the commissioner of the league"""
        if liga.comisionado_id != usuario_id:
            raise ValidationError("Solo el comisionado puede realizar esta acción")
    
    @staticmethod
    def get_liga_current_members_count(liga_id: UUID) -> int:
        """Get the current number of members in a league (excluding commissioner)"""
        return liga_miembro_repository.count_miembros_by_liga(liga_id)
    
    @staticmethod
    def get_liga_total_members_count(liga_id: UUID) -> int:
        """Get the total number of members in a league (including commissioner)"""
        miembros = liga_miembro_repository.get_miembros_by_liga(liga_id)
        return len(miembros)


# Create validator instance
liga_validator = LigaValidator()