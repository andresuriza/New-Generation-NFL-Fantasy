"""
Business logic service for Liga operations with separation of concerns
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from models.database_models import LigaDB, LigaMiembroDB, LigaMiembroAudDB, UsuarioDB, EquipoFantasyDB
from models.liga import (
    LigaCreate, LigaUpdate, LigaResponse, LigaMiembroCreate, 
    LigaMiembroResponse, LigaConMiembros, LigaFilter
)
from repositories.liga_repository import liga_repository, liga_miembro_repository
from services.security_service import security_service
from services.liga_membresia_service import liga_membresia_service
from services.error_handling import handle_db_errors
from validators.liga_validator import LigaValidator
from exceptions.business_exceptions import ValidationError, ConflictError, NotFoundError

def _to_liga_response(liga: LigaDB) -> LigaResponse:
    return LigaResponse.model_validate(liga, from_attributes=True)

def _to_miembro_response(miembro: LigaMiembroDB) -> LigaMiembroResponse:
    return LigaMiembroResponse.model_validate(miembro, from_attributes=True)

class LigaService:
    """Service for Liga CRUD operations"""
    
    @handle_db_errors
    def crear_liga(self, db: Session, liga: LigaCreate) -> LigaResponse:
        """
        Crear una nueva liga con todas las validaciones y configuraciones por defecto.
        
        """
        # Use validator for business rules
        validator = LigaValidator()
        validator.validate_nombre_unique(db, liga.nombre)
        validator.validate_temporada_exists(db, liga.temporada_id)
        validator.validate_comisionado_exists(db, liga.comisionado_id)
        
        # Validate and hash password
        security_service.validate_password_strength(liga.contrasena)
        contrasena_hash = security_service.hash_password(liga.contrasena)
        
        # Prepare league data (exclude nombre_equipo_comisionado as it's not a DB field)
        datos_liga = liga.model_dump(exclude={'contrasena', 'nombre_equipo_comisionado'})
        datos_liga['contrasena_hash'] = contrasena_hash
        
        nueva_liga = LigaDB(**datos_liga)
        
        db.add(nueva_liga)
        db.flush()  # Get ID without full commit
        
        # Create commissioner membership with team name
        self._crear_membresia_comisionado(db, nueva_liga.id, nueva_liga.comisionado_id, liga.nombre_equipo_comisionado)
        
        db.commit()
        db.refresh(nueva_liga)
        return _to_liga_response(nueva_liga)
    
    def _crear_membresia_comisionado(self, db: Session, liga_id: UUID, comisionado_id: UUID, nombre_equipo: str) -> None:
        """Create commissioner membership and corresponding fantasy team"""
        # Skip capacity validation during league creation as commissioner is first member
        
        # Get user alias or use default
        usuario = db.query(UsuarioDB).filter(UsuarioDB.id == comisionado_id).first()
        alias = usuario.alias if usuario and usuario.alias else "Comisionado"
        
        # Create commissioner membership
        membresia_comisionado = LigaMiembroDB(
            liga_id=liga_id,
            usuario_id=comisionado_id,
            alias=alias,
            rol="Comisionado"
        )
        db.add(membresia_comisionado)
        
        # Create commissioner fantasy team with the provided name
        equipo_fantasy_comisionado = EquipoFantasyDB(
            liga_id=liga_id,
            usuario_id=comisionado_id,
            nombre=nombre_equipo
        )
        db.add(equipo_fantasy_comisionado)
        
        # Create audit record
        audit_record = LigaMiembroAudDB(
            liga_id=liga_id,
            usuario_id=comisionado_id,
            accion="unirse"
        )
        db.add(audit_record)
    
    def listar_ligas(self, db: Session, skip: int = 0, limit: int = 100) -> List[LigaResponse]:
        """List all leagues with pagination"""
        ligas = liga_repository.get_multi(db, skip, limit)
        return [_to_liga_response(liga) for liga in ligas]
    
    def buscar_ligas(self, db: Session, filtros: LigaFilter, skip: int = 0, limit: int = 100) -> List[LigaResponse]:
        """Search leagues with filters"""
        ligas = liga_repository.search_with_filter(db, filtros, skip, limit)
        return [_to_liga_response(liga) for liga in ligas]
    
    def obtener_liga(self, db: Session, liga_id: UUID) -> LigaResponse:
        """Get a league by ID"""
        liga = liga_repository.get(db, liga_id)
        if not liga:
            raise NotFoundError("Liga no encontrada")
        return _to_liga_response(liga)
    
    def obtener_liga_con_miembros(self, db: Session, liga_id: UUID) -> LigaConMiembros:
        """Get league with its members"""
        liga = liga_repository.get_with_miembros(db, liga_id)
        if not liga:
            raise NotFoundError("Liga no encontrada")
        
        liga_response = _to_liga_response(liga)
        miembros_response = [_to_miembro_response(m) for m in liga.miembros]
        
        return LigaConMiembros(
            **liga_response.model_dump(),
            miembros=miembros_response
        )
    
    def actualizar_liga(self, db: Session, liga_id: UUID, actualizacion: LigaUpdate) -> LigaResponse:
        """Update a league"""
        validator = LigaValidator()
        liga = validator.validate_exists(db, liga_id)
        validator.validate_liga_editable(liga)
        
        # Validate unique name if changing
        if actualizacion.nombre and actualizacion.nombre != liga.nombre:
            validator.validate_nombre_unique(db, actualizacion.nombre, liga_id)
        
        updated_liga = liga_repository.update(db, liga, actualizacion)
        return _to_liga_response(updated_liga)
    
    def eliminar_liga(self, db: Session, liga_id: UUID) -> bool:
        """Delete a league"""
        validator = LigaValidator()
        liga = validator.validate_exists(db, liga_id)
        validator.validate_liga_editable(liga)
        
        return liga_repository.delete(db, liga_id)
    
    def unirse_liga(self, db: Session, liga_id: UUID, usuario_id: UUID, contrasena: str, alias: str, nombre_equipo: str) -> LigaMiembroResponse:
        """Join a league using the dedicated service"""
        return liga_membresia_service.unirse_liga(db, liga_id, usuario_id, contrasena, alias, nombre_equipo)
    
    def obtener_info_cupos(self, db: Session, liga_id: UUID) -> dict:
        """Get league capacity information"""
        validator = LigaValidator()
        liga = validator.validate_exists(db, liga_id)
        current_members = validator.get_liga_current_members_count(db, liga_id)
        
        return {
            "equipos_max": liga.equipos_max,
            "miembros_actuales": current_members,
            "cupos_disponibles": liga.equipos_max - current_members,
            "esta_llena": current_members >= liga.equipos_max
        }
    
liga_service = LigaService()
