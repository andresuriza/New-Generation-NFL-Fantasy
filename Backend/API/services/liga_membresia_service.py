"""
Business logic service for Liga membership operations
"""
from typing import List
from uuid import UUID

from models.database_models import LigaMiembroDB, LigaMiembroAudDB, EquipoFantasyDB
from models.liga import LigaMiembroResponse, LigaMiembroCreate
from DAL.repositories.liga_repository import liga_miembro_repository, liga_cupo_repository
from DAL.repositories.equipo_fantasy_repository import equipo_fantasy_repository
from DAL.repositories.db_context import db_context
from validators.liga_validator import LigaValidator
from validators.usuario_validator import UsuarioValidator
from services.security_service import security_service

def _to_miembro_response(miembro: LigaMiembroDB) -> LigaMiembroResponse:
    return LigaMiembroResponse.model_validate(miembro, from_attributes=True)

class LigaMembresiaService:
    """Service for handling league membership operations"""
    
    def unirse_liga(self, liga_id: UUID, usuario_id: UUID, contrasena: str, alias: str, nombre_equipo: str) -> LigaMiembroResponse:
        """
        Unirse a una liga.
        """
        # Validate all requirements for joining
        liga_validator = LigaValidator()
        liga = liga_validator.validate_for_join_liga(liga_id, usuario_id, alias, nombre_equipo)
        
        # Verify password
        try:
            password_valid = security_service.verify_password(contrasena, liga.contrasena_hash)
        except Exception as e:
            raise ValueError(f"Error al verificar contraseña: {str(e)}")
        
        # Create membership, fantasy team, and audit record in a single transaction
        with db_context.get_session() as db:
            # Create membership
            nueva_membresia = LigaMiembroDB(
                liga_id=liga_id,
                usuario_id=usuario_id,
                alias=alias,
                rol="Manager"
            )
            
            # Create corresponding fantasy team with the specified team name
            nuevo_equipo_fantasy = EquipoFantasyDB(
                liga_id=liga_id,
                usuario_id=usuario_id,
                nombre=nombre_equipo
            )
            
            # Add audit record
            audit_record = LigaMiembroAudDB(
                liga_id=liga_id,
                usuario_id=usuario_id,
                accion="unirse"
            )
            
            db.add(nueva_membresia)
            db.add(nuevo_equipo_fantasy)
            db.add(audit_record)
            db.flush()
            db.refresh(nueva_membresia)
            
            return _to_miembro_response(nueva_membresia)
    
    def salir_liga(self,liga_id: UUID, usuario_id: UUID) -> bool:
        """Leave a league"""
        # Validate league exists
        liga_validator = LigaValidator()
        liga_validator.validate_exists(liga_id)
        
        # Get membership
        membresia = liga_miembro_repository.get_by_liga_usuario(liga_id, usuario_id)
        if not membresia:
            raise ValueError("No eres miembro de esta liga")
        
        # Prevent commissioner from leaving
        if membresia.rol.value == "Comisionado":
            raise ValueError("El comisionado no puede abandonar la liga")
        
        # Get the corresponding fantasy team
        equipo_fantasy = equipo_fantasy_repository.get_by_liga_and_usuario(liga_id, usuario_id)
        
        try:
            # Add audit record before deleting
            if equipo_fantasy:
                equipo_fantasy_repository.delete(equipo_fantasy.id)
            liga_miembro_repository.delete(membresia.id)
            return True
            
        except Exception as e:
            db.rollback()
            raise ValueError("Error al salir de la liga") from e
    
    def obtener_miembros_liga(self, liga_id: UUID) -> List[LigaMiembroResponse]:
        """Get all members of a league"""
        liga_validator = LigaValidator()
        liga_validator.validate_exists(liga_id)
        miembros = liga_miembro_repository.get_miembros_by_liga(liga_id)
        return [_to_miembro_response(m) for m in miembros]
    
    def cambiar_alias(self, liga_id: UUID, usuario_id: UUID, nuevo_alias: str) -> LigaMiembroResponse:
        """Change user alias in a league"""
        # Validate league exists
        liga_validator = LigaValidator()
        liga_validator.validate_exists(liga_id)
        
        # Get membership
        membresia = liga_miembro_repository.get_by_liga_usuario(liga_id, usuario_id)
        if not membresia:
            raise ValueError("No eres miembro de esta liga")
        
        # Validate new alias is unique
        liga_validator.validate_alias_unique_in_liga(liga_id, nuevo_alias, usuario_id)
        
        # Update alias using repository
        try:
            updated_membresia = liga_miembro_repository.update_alias(membresia.id, nuevo_alias)
            return _to_miembro_response(updated_membresia)
        except Exception as e:
            raise ValueError("Error al cambiar el alias") from e

liga_membresia_service = LigaMembresiaService()