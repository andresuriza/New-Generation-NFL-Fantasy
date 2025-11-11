"""
Equipo NFL validation service
"""
import re
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from models.database_models import EquipoDB
from exceptions.business_exceptions import NotFoundError, ValidationError, ConflictError


class EquipoNFLValidator:
    """Validation service for Equipo NFL model"""
    
    @staticmethod
    def validate_exists(db: Session, equipo_id: UUID) -> EquipoDB:
        """Validate that an NFL team exists"""
        equipo = db.query(EquipoDB).filter(EquipoDB.id == equipo_id).first()
        if not equipo:
            raise NotFoundError("Equipo NFL no encontrado")
        return equipo
    
    @staticmethod
    def validate_nombre_format(nombre: str) -> None:
        """Validate team name format"""
        if not nombre or not nombre.strip():
            raise ValidationError("El nombre del equipo es requerido")
        
        if len(nombre.strip()) < 3:
            raise ValidationError("El nombre del equipo debe tener al menos 3 caracteres")
        
        if len(nombre.strip()) > 100:
            raise ValidationError("El nombre del equipo no puede tener más de 100 caracteres")
        
        # Check for valid characters (letters, spaces, numbers, some special characters)
        if not re.match(r"^[a-zA-ZÀ-ÿ0-9\s\-'\.&]+$", nombre.strip()):
            raise ValidationError("El nombre del equipo contiene caracteres inválidos")
    
    @staticmethod
    def validate_nombre_unique(db: Session, nombre: str, exclude_id: Optional[UUID] = None) -> None:
        """Validate that team name is unique"""
        query = db.query(EquipoDB).filter(EquipoDB.nombre == nombre)
        if exclude_id:
            query = query.filter(EquipoDB.id != exclude_id)
        
        if query.first():
            raise ConflictError(f"El equipo NFL '{nombre}' ya existe")
    
    @staticmethod
    def validate_ciudad_format(ciudad: Optional[str]) -> None:
        """Validate city format"""
        if ciudad is not None and ciudad.strip():
            if len(ciudad.strip()) < 2:
                raise ValidationError("El nombre de la ciudad debe tener al menos 2 caracteres")
            
            if len(ciudad.strip()) > 100:
                raise ValidationError("El nombre de la ciudad no puede tener más de 100 caracteres")
            
            # Check for valid characters (letters, spaces, hyphens, apostrophes)
            if not re.match(r"^[a-zA-ZÀ-ÿ\s\-'\.]+$", ciudad.strip()):
                raise ValidationError("El nombre de la ciudad contiene caracteres inválidos")
    
    @staticmethod
    def validate_thumbnail_url_format(thumbnail: Optional[str]) -> None:
        """Validate thumbnail URL format"""
        if thumbnail is not None and thumbnail.strip():
            # Basic URL validation
            url_pattern = r'^https?:\/\/.*\.(jpg|jpeg|png|gif|webp|svg)$'
            if not re.match(url_pattern, thumbnail.strip(), re.IGNORECASE):
                raise ValidationError("URL de thumbnail inválida. Debe ser una URL válida con extensión de imagen")
    
    @staticmethod
    def validate_abreviacion_format(abreviacion: Optional[str]) -> None:
        """Validate team abbreviation format"""
        if abreviacion is not None and abreviacion.strip():
            if len(abreviacion.strip()) < 2:
                raise ValidationError("La abreviación debe tener al menos 2 caracteres")
            
            if len(abreviacion.strip()) > 5:
                raise ValidationError("La abreviación no puede tener más de 5 caracteres")
            
            # Check for uppercase letters only
            if not re.match(r"^[A-Z]+$", abreviacion.strip()):
                raise ValidationError("La abreviación debe contener solo letras mayúsculas")
    
    @staticmethod
    def validate_abreviacion_unique(db: Session, abreviacion: str, exclude_id: Optional[UUID] = None) -> None:
        """Validate that team abbreviation is unique"""
        if abreviacion and abreviacion.strip():
            query = db.query(EquipoDB).filter(EquipoDB.abreviacion == abreviacion.strip())
            if exclude_id:
                query = query.filter(EquiposDB.id != exclude_id)
            
            if query.first():
                raise ConflictError(f"La abreviación '{abreviacion}' ya existe")
    
    @staticmethod
    def validate_equipo_can_be_deleted(db: Session, equipo_id: UUID) -> None:
        """Validate that NFL team can be deleted"""
        from models.database_models import JugadoresDB
        
        # Check if team has players
        players_count = db.query(JugadoresDB).filter(JugadoresDB.equipo_nfl_id == equipo_id).count()
        if players_count > 0:
            raise ValidationError("No se puede eliminar el equipo NFL porque tiene jugadores asociados")
    
    @staticmethod
    def validate_division_format(division: Optional[str]) -> None:
        """Validate NFL division format"""
        if division is not None and division.strip():
            valid_divisions = [
                "AFC North", "AFC South", "AFC East", "AFC West",
                "NFC North", "NFC South", "NFC East", "NFC West"
            ]
            
            if division.strip() not in valid_divisions:
                raise ValidationError(f"División inválida. Divisiones válidas: {', '.join(valid_divisions)}")
    
    @staticmethod
    def validate_conference_format(conference: Optional[str]) -> None:
        """Validate NFL conference format"""
        if conference is not None and conference.strip():
            valid_conferences = ["AFC", "NFC"]
            
            if conference.strip() not in valid_conferences:
                raise ValidationError(f"Conferencia inválida. Conferencias válidas: {', '.join(valid_conferences)}")
    
    @staticmethod
    def validate_equipo_can_be_deleted(equipo: EquipoDB) -> None:
        """Validate that an NFL team can be deleted (no associated players)"""
        if equipo.jugadores:
            raise ValidationError("No se puede eliminar el equipo NFL porque tiene jugadores asociados")


# Create validator instance
equipo_nfl_validator = EquipoNFLValidator()