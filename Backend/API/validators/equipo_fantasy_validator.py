"""
Equipo Fantasy validation service
"""
import re
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from models.database_models import EquipoFantasyDB, UsuarioDB, LigaDB
from exceptions.business_exceptions import NotFoundError, ValidationError, ConflictError


class EquipoFantasyValidator:
    """Validation service for Equipo Fantasy model"""
    
    @staticmethod
    def validate_exists(db: Session, equipo_id: UUID) -> EquipoFantasyDB:
        """Validate that a fantasy team exists"""
        equipo = db.query(EquipoFantasyDB).filter(EquipoFantasyDB.id == equipo_id).first()
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
    def validate_nombre_unique_in_liga(db: Session, nombre: str, liga_id: UUID, exclude_id: Optional[UUID] = None) -> None:
        """Validate that fantasy team name is unique within the league"""
        query = db.query(EquipoFantasyDB).filter(
            EquipoFantasyDB.nombre == nombre,
            EquipoFantasyDB.liga_id == liga_id
        )
        
        if exclude_id:
            query = query.filter(EquipoFantasyDB.id != exclude_id)
        
        existing_team = query.first()
        if existing_team:
            raise ConflictError("Ya existe un equipo con ese nombre en la liga")
    
    @staticmethod
    def validate_usuario_exists(db: Session, usuario_id: UUID) -> UsuarioDB:
        """Validate that user exists and is active"""
        usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
        if not usuario:
            raise NotFoundError("Usuario no encontrado")
        
        if usuario.estado.value != "activa":
            raise ValidationError("El usuario debe estar activo")
        
        return usuario
    
    @staticmethod
    def validate_liga_exists(db: Session, liga_id: UUID) -> LigaDB:
        """Validate that league exists"""
        liga = db.query(LigaDB).filter(LigaDB.id == liga_id).first()
        if not liga:
            raise NotFoundError("Liga no encontrada")
        return liga
    
    @staticmethod
    def validate_usuario_in_liga(db: Session, usuario_id: UUID, liga_id: UUID) -> None:
        """Validate that user is a member of the league"""
        from models.database_models import LigaMiembroDB
        
        miembro = db.query(LigaMiembroDB).filter(
            LigaMiembroDB.usuario_id == usuario_id,
            LigaMiembroDB.liga_id == liga_id
        ).first()
        
        if not miembro:
            raise ValidationError("El usuario debe ser miembro de la liga")
    
    @staticmethod
    def validate_usuario_not_has_team_in_liga(db: Session, usuario_id: UUID, liga_id: UUID, exclude_id: Optional[UUID] = None) -> None:
        """Validate that user doesn't already have a team in this league"""
        query = db.query(EquipoFantasyDB).filter(
            EquipoFantasyDB.usuario_id == usuario_id,
            EquipoFantasyDB.liga_id == liga_id
        )
        
        if exclude_id:
            query = query.filter(EquipoFantasyDB.id != exclude_id)
        
        existing_team = query.first()
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
    def validate_equipo_can_be_deleted(db: Session, equipo_id: UUID) -> None:
        """Validate that fantasy team can be deleted"""
        equipo = EquipoFantasyValidator.validate_exists(db, equipo_id)
        
        # Check if league allows deletions
        liga = db.query(LigaDB).filter(LigaDB.id == equipo.liga_id).first()
        if liga and liga.estado.value != "Pre_draft":
            raise ValidationError("No se puede eliminar el equipo después del draft")


# Create validator instance
equipo_fantasy_validator = EquipoFantasyValidator()