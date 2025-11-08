"""
Liga validation service
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from models.database_models import LigaDB, LigaMiembroDB, UsuarioDB, TemporadaDB
from exceptions.business_exceptions import NotFoundError, ValidationError, ConflictError


class LigaValidator:
    """Validation service for Liga model"""
    
    @staticmethod
    def validate_exists(db: Session, liga_id: UUID) -> LigaDB:
        """Validate that a league exists"""
        liga = db.query(LigaDB).filter(LigaDB.id == liga_id).first()
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
    def validate_nombre_unique(db: Session, nombre: str, exclude_id: Optional[UUID] = None) -> None:
        """Validate that league name is unique"""
        query = db.query(LigaDB).filter(LigaDB.nombre == nombre)
        if exclude_id:
            query = query.filter(LigaDB.id != exclude_id)
        
        if query.first():
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
    def validate_comisionado_exists(db: Session, comisionado_id: UUID) -> UsuarioDB:
        """Validate that commissioner exists and is active"""
        comisionado = db.query(UsuarioDB).filter(UsuarioDB.id == comisionado_id).first()
        if not comisionado:
            raise NotFoundError("Usuario comisionado no encontrado")
        
        if comisionado.estado.value != "activa":
            raise ValidationError("El comisionado debe ser un usuario activo")
        
        return comisionado
    
    @staticmethod
    def validate_temporada_exists(db: Session, temporada_id: UUID) -> TemporadaDB:
        """Validate that season exists"""
        temporada = db.query(TemporadaDB).filter(TemporadaDB.id == temporada_id).first()
        if not temporada:
            raise NotFoundError("Temporada no encontrada")
        
        return temporada
    
    @staticmethod
    def validate_liga_editable(liga: LigaDB) -> None:
        """Validate that a league can be edited (only in Pre_draft state)"""
        if liga.estado.value != "Pre_draft":
            raise ValidationError("Solo se pueden modificar ligas en estado Pre_draft")
    
    @staticmethod
    def validate_liga_has_cupos(db: Session, liga_id: UUID) -> None:
        """Validate that a league has available spots"""
        # Get the league to check equipos_max
        liga = db.query(LigaDB).filter(LigaDB.id == liga_id).first()
        if not liga:
            raise NotFoundError("Liga no encontrada")
        
        # Count current members in the league (excluding comisionado)
        # Only count members with Manager role, as Commissioner doesn't count towards limit
        from models.database_models import RolMembresiaEnum
        current_members_count = db.query(LigaMiembroDB).filter(
            LigaMiembroDB.liga_id == liga_id,
            LigaMiembroDB.rol == RolMembresiaEnum.Manager
        ).count()
        
        # Check if league is full (use equipos_max as the limit, comisionado doesn't count)
        if current_members_count >= liga.equipos_max:
            raise ValidationError("La liga está llena")
    
    @staticmethod
    def validate_usuario_not_in_liga(db: Session, liga_id: UUID, usuario_id: UUID) -> None:
        """Validate that a user is not already in the league"""
        miembro_existente = db.query(LigaMiembroDB).filter(
            LigaMiembroDB.liga_id == liga_id,
            LigaMiembroDB.usuario_id == usuario_id
        ).first()
        
        if miembro_existente:
            raise ConflictError("Ya eres miembro de esta liga")
    
    @staticmethod
    def validate_alias_unique_in_liga(db: Session, liga_id: UUID, alias: str, exclude_usuario_id: Optional[UUID] = None) -> None:
        """Validate that an alias is unique within a league"""
        query = db.query(LigaMiembroDB).filter(
            LigaMiembroDB.liga_id == liga_id,
            LigaMiembroDB.alias == alias
        )
        
        if exclude_usuario_id:
            query = query.filter(LigaMiembroDB.usuario_id != exclude_usuario_id)
        
        if query.first():
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
    def validate_codigo_invitacion_unique(db: Session, codigo: str, exclude_id: Optional[UUID] = None) -> None:
        """Validate that invitation code is unique"""
        query = db.query(LigaDB).filter(LigaDB.codigo_invitacion == codigo)
        if exclude_id:
            query = query.filter(LigaDB.id != exclude_id)
        
        if query.first():
            raise ConflictError("El código de invitación ya existe")
    
    @staticmethod
    def validate_liga_can_be_deleted(db: Session, liga_id: UUID) -> None:
        """Validate that league can be deleted"""
        # Check if league has any members (including commissioner)
        total_members_count = db.query(LigaMiembroDB).filter(LigaMiembroDB.liga_id == liga_id).count()
        if total_members_count > 0:
            raise ValidationError("No se puede eliminar la liga porque tiene miembros")
    
    @staticmethod
    def validate_usuario_is_comisionado(liga: LigaDB, usuario_id: UUID) -> None:
        """Validate that user is the commissioner of the league"""
        if liga.comisionado_id != usuario_id:
            raise ValidationError("Solo el comisionado puede realizar esta acción")
    
    @staticmethod
    def get_liga_current_members_count(db: Session, liga_id: UUID) -> int:
        """Get the current number of members in a league (excluding commissioner)"""
        from models.database_models import RolMembresiaEnum
        return db.query(LigaMiembroDB).filter(
            LigaMiembroDB.liga_id == liga_id,
            LigaMiembroDB.rol == RolMembresiaEnum.Manager
        ).count()
    
    @staticmethod
    def get_liga_total_members_count(db: Session, liga_id: UUID) -> int:
        """Get the total number of members in a league (including commissioner)"""
        return db.query(LigaMiembroDB).filter(LigaMiembroDB.liga_id == liga_id).count()


# Create validator instance
liga_validator = LigaValidator()