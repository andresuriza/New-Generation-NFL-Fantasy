"""
Service for NFL Teams (Equipos) operations
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from models.database_models import EquipoDB
from models.equipo import EquipoNFLCreate, EquipoNFLUpdate, EquipoNFLResponse, EquipoNFLConMedia
from repositories.equipo_repository import equipo_repository
from services.error_handling import handle_db_errors
from validators.equipo_nfl_validator import EquipoNFLValidator
from exceptions.business_exceptions import ValidationError, ConflictError, NotFoundError

def _to_response(e: EquipoDB) -> EquipoNFLResponse:
    """Convert EquipoDB to response model"""
    return EquipoNFLResponse.model_validate(e, from_attributes=True)

def _to_response_con_media(e: EquipoDB) -> EquipoNFLConMedia:
    """Convert EquipoDB to response with media"""
    media_url = e.media.url if e.media else None
    response_data = EquipoNFLResponse.model_validate(e, from_attributes=True).model_dump()
    response_data['media_url'] = media_url
    return EquipoNFLConMedia(**response_data)


class EquipoNFLService:
    """Service for NFL Team CRUD operations"""
    
    @handle_db_errors
    def crear_equipo(self, db: Session, equipo: EquipoNFLCreate) -> EquipoNFLResponse:
        """Create a new NFL team"""
        # Use validator for name uniqueness check
        validator = EquipoNFLValidator()
        validator.validate_nombre_unique(db, equipo.nombre)
        
        nuevo_equipo = equipo_repository.create(db, equipo)
        return _to_response(nuevo_equipo)

    def listar(self, db: Session) -> List[EquipoNFLResponse]:
        """List all NFL teams"""
        items = db.query(EquipoDB).all()
        return [_to_response(e) for e in items]

    def obtener(self, db: Session, equipo_id: UUID) -> EquipoNFLResponse:
        """Get NFL team by ID"""
        equipo = equipo_repository.get(db, equipo_id)
        if not equipo:
            raise NotFoundError("Equipo NFL no encontrado")
        return _to_response(equipo)

    def obtener_con_media(self, db: Session, equipo_id: UUID) -> EquipoNFLConMedia:
        """Get NFL team by ID with media information"""
        equipo = equipo_repository.get(db, equipo_id)
        if not equipo:
            raise NotFoundError("Equipo NFL no encontrado")
        return _to_response_con_media(equipo)

    @handle_db_errors
    def actualizar(self, db: Session, equipo_id: UUID, equipo_update: EquipoNFLUpdate) -> EquipoNFLResponse:
        """Update NFL team"""
        validator = EquipoNFLValidator()
        equipo_existente = validator.validate_exists(db, equipo_id)
        
        # Check if new name already exists (if name is being changed)
        if equipo_update.nombre and equipo_update.nombre != equipo_existente.nombre:
            validator.validate_nombre_unique(db, equipo_update.nombre, equipo_id)
        
        equipo_actualizado = equipo_repository.update(db, equipo_id, equipo_update)
        return _to_response(equipo_actualizado)

    @handle_db_errors
    def eliminar(self, db: Session, equipo_id: UUID) -> None:
        """Delete NFL team"""
        validator = EquipoNFLValidator()
        equipo = validator.validate_exists(db, equipo_id)
        
        # Check if team has players (should not delete if it has active relationships)
        validator.validate_equipo_can_be_deleted(equipo)
        
        equipo_repository.delete(db, equipo_id)


# Create service instance
equipo_service = EquipoNFLService()
