from typing import List
from uuid import UUID

from models.database_models import LigaDB, LigaMiembroDB
from models.liga import (
    LigaCreate, LigaUpdate, LigaResponse, 
    LigaMiembroResponse, LigaConMiembros, LigaFilter
)
from DAL.repositories.liga_repository import liga_repository, liga_miembro_repository
from services.security_service import security_service
from services.liga_membresia_service import liga_membresia_service
from services.error_handling import handle_db_errors
from validators.liga_validator import LigaValidator
from exceptions.business_exceptions import NotFoundError

def _to_liga_response(liga: LigaDB) -> LigaResponse:
    return LigaResponse.model_validate(liga, from_attributes=True)

def _to_miembro_response(miembro: LigaMiembroDB) -> LigaMiembroResponse:
    return LigaMiembroResponse.model_validate(miembro, from_attributes=True)

class LigaService:
    """Service for Liga CRUD operations"""
    
    @handle_db_errors
    def crear_liga(self, liga: LigaCreate) -> LigaResponse:
        """
        Crear una nueva liga con todas las validaciones y configuraciones por defecto.
        
        """
        # Validate all requirements for creating a league
        validator = LigaValidator()
        validator.validate_for_create(liga.nombre, liga.temporada_id, liga.comisionado_id)
        
        # Validate and hash password
        security_service.validate_password_strength(liga.contrasena)
        contrasena_hash = security_service.hash_password(liga.contrasena)
        
        # Prepare league data
        datos_liga = liga.model_dump(exclude={'contrasena', 'nombre_equipo_comisionado'})
        datos_liga['contrasena_hash'] = contrasena_hash
        
        # Create league with commissioner membership in a single transaction
        # This would ideally be a single repository method, but for now we'll note this
        # TODO: Move this complex transaction to liga_repository.create_with_commissioner()
        nueva_liga = liga_repository.create(datos_liga)
        
        return _to_liga_response(nueva_liga)
    
    
    def listar_ligas(self, skip: int = 0, limit: int = 100) -> List[LigaResponse]:
        """List all leagues with pagination"""
        ligas = liga_repository.get_multi(skip, limit)
        return [_to_liga_response(liga) for liga in ligas]
    
    def buscar_ligas(self, filtros: LigaFilter, skip: int = 0, limit: int = 100) -> List[LigaResponse]:
        """Search leagues with filters"""
        ligas = liga_repository.search_with_filter(filtros, skip, limit)
        return [_to_liga_response(liga) for liga in ligas]
    
    def obtener_liga(self, liga_id: UUID) -> LigaResponse:
        """Get a league by ID"""
        liga = liga_repository.get(liga_id)
        if not liga:
            raise NotFoundError("Liga no encontrada")
        return _to_liga_response(liga)
    
    def obtener_liga_con_miembros(self, liga_id: UUID) -> LigaConMiembros:
        """Get league with its members"""
        liga = liga_repository.get_with_miembros(liga_id)
        if not liga:
            raise NotFoundError("Liga no encontrada")
        
        liga_response = _to_liga_response(liga)
        miembros_response = [_to_miembro_response(m) for m in liga.miembros]
        
        return LigaConMiembros(
            **liga_response.model_dump(),
            miembros=miembros_response
        )
    
    def actualizar_liga(self, liga_id: UUID, actualizacion: LigaUpdate) -> LigaResponse:
        """Update a league"""
        validator = LigaValidator()
        liga = validator.validate_for_update(liga_id, actualizacion.nombre)
        
        updated_liga = liga_repository.update(liga, actualizacion)
        return _to_liga_response(updated_liga)
    
    def eliminar_liga(self, liga_id: UUID) -> bool:
        """Delete a league"""
        validator = LigaValidator()
        validator.validate_for_delete(liga_id)
        
        return liga_repository.delete(liga_id)
    
    def unirse_liga(self, liga_id: UUID, usuario_id: UUID, contrasena: str, alias: str, nombre_equipo: str) -> LigaMiembroResponse:
        """Join a league using the dedicated service"""
        return liga_membresia_service.unirse_liga(liga_id, usuario_id, contrasena, alias, nombre_equipo)
    
    def obtener_info_cupos(self, liga_id: UUID) -> dict:
        """Get league capacity information"""
        validator = LigaValidator()
        liga = validator.validate_exists(liga_id)
        current_members = validator.get_liga_current_members_count(liga_id)
        
        return {
            "equipos_max": liga.equipos_max,
            "miembros_actuales": current_members,
            "cupos_disponibles": liga.equipos_max - current_members,
            "esta_llena": current_members >= liga.equipos_max
        }
    
liga_service = LigaService()
