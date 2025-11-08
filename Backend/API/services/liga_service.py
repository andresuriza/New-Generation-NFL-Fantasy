"""
Business logic service for Liga operations with separation of concerns
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.database_models import LigaDB, LigaMiembroDB, LigaMiembroAudDB, UsuarioDB, EquipoFantasyDB
from models.liga import (
    LigaCreate, LigaUpdate, LigaResponse, LigaMiembroCreate, 
    LigaMiembroResponse, LigaConMiembros
)
from repositories.liga_repository import liga_repository, liga_miembro_repository
from services.validation_service import validation_service
from services.security_service import security_service
from services.liga_membresia_service import liga_membresia_service

def _to_liga_response(liga: LigaDB) -> LigaResponse:
    return LigaResponse.model_validate(liga, from_attributes=True)

def _to_miembro_response(miembro: LigaMiembroDB) -> LigaMiembroResponse:
    return LigaMiembroResponse.model_validate(miembro, from_attributes=True)

class LigaService:
    """Service for Liga CRUD operations"""
    
    def crear_liga(self, db: Session, liga: LigaCreate) -> LigaResponse:
        """Create a new league"""
        # Validate business rules
        validation_service.validate_liga_nombre_unique(db, liga.nombre)
        validation_service.validate_temporada_exists(db, liga.temporada_id)
        validation_service.validate_usuario_exists(db, liga.comisionado_id)
        
        # Validate and hash password
        security_service.validate_password_strength(liga.contrasena)
        contrasena_hash = security_service.hash_password(liga.contrasena)
        
        # Prepare league data
        datos_liga = liga.model_dump(exclude={'contrasena'})
        datos_liga['contrasena_hash'] = contrasena_hash
        
        nueva_liga = LigaDB(**datos_liga)
        
        try:
            db.add(nueva_liga)
            db.flush()  # Get ID without full commit
            
            # Create commissioner membership
            self._crear_membresia_comisionado(db, nueva_liga.id, nueva_liga.comisionado_id)
            
            db.commit()
            db.refresh(nueva_liga)
            return _to_liga_response(nueva_liga)
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error al crear la liga"
            ) from e
    
    def _crear_membresia_comisionado(self, db: Session, liga_id: UUID, comisionado_id: UUID) -> None:
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
        
        # Create commissioner fantasy team
        equipo_fantasy_comisionado = EquipoFantasyDB(
            liga_id=liga_id,
            usuario_id=comisionado_id,
            nombre=alias  # Use alias as team name
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
    
    def obtener_liga(self, db: Session, liga_id: UUID) -> LigaResponse:
        """Get a league by ID"""
        liga = liga_repository.get(db, liga_id)
        if not liga:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Liga no encontrada"
            )
        return _to_liga_response(liga)
    
    def obtener_liga_con_miembros(self, db: Session, liga_id: UUID) -> LigaConMiembros:
        """Get league with its members"""
        liga = liga_repository.get_with_miembros(db, liga_id)
        if not liga:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Liga no encontrada"
            )
        
        liga_response = _to_liga_response(liga)
        miembros_response = [_to_miembro_response(m) for m in liga.miembros]
        
        return LigaConMiembros(
            **liga_response.model_dump(),
            miembros=miembros_response
        )
    
    def actualizar_liga(self, db: Session, liga_id: UUID, actualizacion: LigaUpdate) -> LigaResponse:
        """Update a league"""
        liga = validation_service.validate_liga_exists(db, liga_id)
        validation_service.validate_liga_editable(liga)
        
        # Validate unique name if changing
        if actualizacion.nombre and actualizacion.nombre != liga.nombre:
            validation_service.validate_liga_nombre_unique(db, actualizacion.nombre, liga_id)
        
        updated_liga = liga_repository.update(db, liga, actualizacion)
        return _to_liga_response(updated_liga)
    
    def eliminar_liga(self, db: Session, liga_id: UUID) -> bool:
        """Delete a league"""
        liga = validation_service.validate_liga_exists(db, liga_id)
        validation_service.validate_liga_editable(liga)
        
        return liga_repository.delete(db, liga_id)
    
    def unirse_liga(self, db: Session, liga_id: UUID, usuario_id: UUID, contrasena: str, alias: str) -> LigaMiembroResponse:
        """Join a league using the dedicated service"""
        return liga_membresia_service.unirse_liga(db, liga_id, usuario_id, contrasena, alias)
    
    def obtener_info_cupos(self, db: Session, liga_id: UUID) -> dict:
        """Get league capacity information"""
        liga = validation_service.validate_liga_exists(db, liga_id)
        current_members = validation_service.get_liga_current_members_count(db, liga_id)
        
        return {
            "equipos_max": liga.equipos_max,
            "miembros_actuales": current_members,
            "cupos_disponibles": liga.equipos_max - current_members,
            "esta_llena": current_members >= liga.equipos_max
        }
    
liga_service = LigaService()
