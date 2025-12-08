"""
Business logic service for Temporada operations with separation of concerns
"""
from typing import List, Optional
from uuid import UUID
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
from DAL.repositories.temporada_repository import temporada_repository, temporada_semana_repository
from DAL.repositories.liga_repository import liga_repository
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
    def crear_temporada(self, temporada: TemporadaCreate) -> TemporadaResponse:
        """Create a new season"""
        # Use validator for all validations
        TemporadaValidator.validate_complete_season_creation(
            temporada.nombre,
            temporada.semanas,
            temporada.fecha_inicio,
            temporada.fecha_fin,
            temporada.es_actual
        )
        
        # Handle current season logic
        if temporada.es_actual:
            temporada_repository.unset_all_actual()
        
        nueva_temporada = temporada_repository.create(temporada)
        return _to_temporada_response(nueva_temporada)
    
    def listar_temporadas(self) -> List[TemporadaResponse]:
        """List all seasons"""
        temporadas = temporada_repository.get_all_ordered()
        return [_to_temporada_response(t) for t in temporadas]
    
    def obtener_temporada(self, temporada_id: UUID) -> TemporadaResponse:
        """Get a season by ID"""
        temporada = temporada_repository.get(temporada_id)
        if not temporada:
            raise NotFoundError("Temporada no encontrada")
        return _to_temporada_response(temporada)
    
    def obtener_temporada_actual(self) -> TemporadaResponse:
        """Get current active season"""
        temporada = temporada_repository.get_actual()
        if not temporada:
            raise NotFoundError("No hay temporada actual definida")
        return _to_temporada_response(temporada)
    
    @handle_db_errors
    def actualizar_temporada(self, temporada_id: UUID, actualizacion: TemporadaUpdate) -> TemporadaResponse:
        """Actualizar una temporada"""
        temporada = temporada_repository.get(temporada_id)
        
        if not temporada:
            raise NotFoundError("Temporada no encontrada")
        
        # Validate all requirements for updating
        datos_actualizados = actualizacion.model_dump(exclude_unset=True)
        TemporadaValidator.validate_for_update(
            temporada_id,
            fecha_inicio=datos_actualizados.get("fecha_inicio"),
            fecha_fin=datos_actualizados.get("fecha_fin"),
            semanas=datos_actualizados.get("semanas")
        )
        
        # Si se marca como actual, desmarcar otras temporadas actuales
        if actualizacion.es_actual:
            temporada_repository.unset_all_actual()
        
        temporada_actualizada = temporada_repository.update(temporada_id, actualizacion)
        return _to_temporada_response(temporada_actualizada)
    
    @handle_db_errors
    def eliminar_temporada(self, temporada_id: UUID) -> bool:
        """Delete a season"""
        temporada = temporada_repository.get(temporada_id)
        if not temporada:
            raise NotFoundError("Temporada no encontrada")
        
        # Check for associated leagues
        if liga_repository.has_associated_ligas(temporada_id):
            raise ValidationError("No se puede eliminar la temporada porque tiene ligas asociadas")
        
        return temporada_repository.delete(temporada_id)
    
    @handle_db_errors
    def crear_semana(self, semana: TemporadaSemanaCreate) -> TemporadaSemanaResponse:
        """Crear una semana para una temporada"""
        # Use validator for week creation
        TemporadaValidator.validate_week_creation(
            semana.temporada_id,
            semana.numero,
            semana.fecha_inicio,
            semana.fecha_fin
        )
        
        nueva_semana = temporada_semana_repository.create(semana)
        
        return _to_semana_response(nueva_semana)
    
    def obtener_temporada_con_semanas(self, temporada_id: UUID) -> TemporadaConSemanas:
        """Obtener temporada con sus semanas"""
        temporada = temporada_repository.get(temporada_id)
        
        if not temporada:
            raise NotFoundError("Temporada no encontrada")
        
        semanas = temporada_semana_repository.get_by_temporada(temporada_id)
        
        temporada_response = _to_temporada_response(temporada)
        semanas_response = [_to_semana_response(s) for s in semanas]
        
        return TemporadaConSemanas(
            **temporada_response.model_dump(),
            semanas_detalle=semanas_response
        )


temporada_service = TemporadaService()