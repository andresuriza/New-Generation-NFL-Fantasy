"""
Business logic service for Temporada operations with separation of concerns
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.database_models import TemporadaDB, TemporadaSemanaDB
from models.temporada import (
    TemporadaResponse, 
    TemporadaCreate, 
    TemporadaUpdate,
    TemporadaSemanaResponse,
    TemporadaSemanaCreate,
    TemporadaConSemanas
)
from repositories.temporada_repository import temporada_repository, temporada_semana_repository
from repositories.liga_repository import liga_repository
from services.error_handling import handle_db_errors
from validators.temporada_validator import TemporadaValidator
from exceptions.business_exceptions import ValidationError, ConflictError, NotFoundError


def _to_temporada_response(temporada: TemporadaDB) -> TemporadaResponse:
    return TemporadaResponse.model_validate(temporada, from_attributes=True)


def _to_semana_response(semana: TemporadaSemanaDB) -> TemporadaSemanaResponse:
    return TemporadaSemanaResponse.model_validate(semana, from_attributes=True)


class TemporadaService:
    """Service for Temporada CRUD operations"""
    
    @handle_db_errors
    def crear_temporada(self, db: Session, temporada: TemporadaCreate) -> TemporadaResponse:
        """Create a new season"""
        # Use validator for all validations
        validator = TemporadaValidator(db)
        validator.validate_complete_season_creation(temporada)
        
        # Handle current season logic
        if temporada.es_actual:
            temporada_repository.unset_all_actual(db)
        
        nueva_temporada = temporada_repository.create(db, temporada)
        return _to_temporada_response(nueva_temporada)
    
    def listar_temporadas(self, db: Session) -> List[TemporadaResponse]:
        """List all seasons"""
        temporadas = temporada_repository.get_all_ordered(db)
        return [_to_temporada_response(t) for t in temporadas]
    
    def obtener_temporada(self, db: Session, temporada_id: UUID) -> TemporadaResponse:
        """Get a season by ID"""
        temporada = temporada_repository.get(db, temporada_id)
        if not temporada:
            raise NotFoundError("Temporada no encontrada")
        return _to_temporada_response(temporada)
    
    def obtener_temporada_actual(self, db: Session) -> TemporadaResponse:
        """Get current active season"""
        temporada = temporada_repository.get_actual(db)
        if not temporada:
            raise NotFoundError("No hay temporada actual definida")
        return _to_temporada_response(temporada)
    
    @handle_db_errors
    def actualizar_temporada(self, db: Session, temporada_id: UUID, actualizacion: TemporadaUpdate) -> TemporadaResponse:
        """Actualizar una temporada"""
        temporada = db.query(TemporadaDB).filter(TemporadaDB.id == temporada_id).first()
        
        if not temporada:
            raise NotFoundError("Temporada no encontrada")
        
        # Use validator for validations
        validator = TemporadaValidator(db)
        
        # Validate updates if date range or weeks are being updated
        datos_actualizados = actualizacion.model_dump(exclude_unset=True)
        if "fecha_inicio" in datos_actualizados or "fecha_fin" in datos_actualizados:
            fecha_inicio = datos_actualizados.get("fecha_inicio", temporada.fecha_inicio)
            fecha_fin = datos_actualizados.get("fecha_fin", temporada.fecha_fin)
            validator.validate_fecha_fin_posterior_inicio(fecha_inicio, fecha_fin)
        
        if "semanas" in datos_actualizados:
            validator.validate_weeks_count_range(datos_actualizados["semanas"])
        
        # Si se marca como actual, desmarcar otras temporadas actuales
        if actualizacion.es_actual:
            db.query(TemporadaDB).filter(
                TemporadaDB.es_actual == True,
                TemporadaDB.id != temporada_id
            ).update({"es_actual": False})
        
        for campo, valor in datos_actualizados.items():
            setattr(temporada, campo, valor)
        
        db.commit()
        db.refresh(temporada)
        return _to_temporada_response(temporada)
    
    @handle_db_errors
    def eliminar_temporada(self, db: Session, temporada_id: UUID) -> bool:
        """Delete a season"""
        temporada = temporada_repository.get(db, temporada_id)
        if not temporada:
            raise NotFoundError("Temporada no encontrada")
        
        # Check for associated leagues
        if liga_repository.has_associated_ligas(db, temporada_id):
            raise ValidationError("No se puede eliminar la temporada porque tiene ligas asociadas")
        
        return temporada_repository.delete(db, temporada_id)
    
    @handle_db_errors
    def crear_semana(self, db: Session, semana: TemporadaSemanaCreate) -> TemporadaSemanaResponse:
        """Crear una semana para una temporada"""
        # Use validator for week creation
        validator = TemporadaValidator(db)
        validator.validate_week_creation(semana)
        
        nueva_semana = TemporadaSemanaDB(**semana.model_dump())
        
        db.add(nueva_semana)
        db.commit()
        db.refresh(nueva_semana)
        return _to_semana_response(nueva_semana)
    
    def obtener_temporada_con_semanas(self, db: Session, temporada_id: UUID) -> TemporadaConSemanas:
        """Obtener temporada con sus semanas"""
        temporada = db.query(TemporadaDB).filter(TemporadaDB.id == temporada_id).first()
        
        if not temporada:
            raise NotFoundError("Temporada no encontrada")
        
        semanas = db.query(TemporadaSemanaDB).filter(
            TemporadaSemanaDB.temporada_id == temporada_id
        ).order_by(TemporadaSemanaDB.numero).all()
        
        temporada_response = _to_temporada_response(temporada)
        semanas_response = [_to_semana_response(s) for s in semanas]
        
        return TemporadaConSemanas(
            **temporada_response.model_dump(),
            semanas_detalle=semanas_response
        )


temporada_service = TemporadaService()