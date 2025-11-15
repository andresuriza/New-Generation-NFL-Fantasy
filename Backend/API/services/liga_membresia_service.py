"""
Business logic service for Liga membership operations
"""
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.database_models import LigaMiembroDB, LigaMiembroAudDB, EquipoFantasyDB
from models.liga import LigaMiembroResponse, LigaMiembroCreate
from repositories.liga_repository import liga_miembro_repository, liga_cupo_repository
from validators.liga_validator import LigaValidator
from validators.usuario_validator import UsuarioValidator
from services.security_service import security_service

def _to_miembro_response(miembro: LigaMiembroDB) -> LigaMiembroResponse:
    return LigaMiembroResponse.model_validate(miembro, from_attributes=True)

class LigaMembresiaService:
    """Service for handling league membership operations"""
    
    def unirse_liga(self, db: Session, liga_id: UUID, usuario_id: UUID, contrasena: str, alias: str, nombre_equipo: str) -> LigaMiembroResponse:
        """
        Unirse a una liga.
        """
        # Use validators
        liga_validator = LigaValidator()
        usuario_validator = UsuarioValidator()
        
        # Validate league exists and get it
        liga = liga_validator.validate_exists(db, liga_id)
        
        # Verify password
        try:
            password_valid = security_service.verify_password(contrasena, liga.contrasena_hash)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al verificar contraseña: {str(e)}"
            )
        
        if not password_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Contraseña de liga incorrecta"
            )
        
        # Validate user is not already in league
        liga_validator.validate_usuario_not_in_liga(db, liga_id, usuario_id)
        
        # Validate league has available spots
        liga_validator.validate_liga_has_cupos(db, liga_id)
        
        # Validate alias is unique in league
        liga_validator.validate_alias_unique_in_liga(db, liga_id, alias)
        
        # Validate team name is unique in league
        from validators.equipo_fantasy_validator import EquipoFantasyValidator
        equipo_validator = EquipoFantasyValidator()
        equipo_validator.validate_nombre_unique_in_liga(db, nombre_equipo, liga_id)
        
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
        
        try:
            db.add(nueva_membresia)
            db.add(nuevo_equipo_fantasy)
            
            # Add audit record
            audit_record = LigaMiembroAudDB(
                liga_id=liga_id,
                usuario_id=usuario_id,
                accion="unirse"
            )
            db.add(audit_record)
            
            db.commit()
            db.refresh(nueva_membresia)
            return _to_miembro_response(nueva_membresia)
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error al unirse a la liga"
            ) from e
    
    def salir_liga(self, db: Session, liga_id: UUID, usuario_id: UUID) -> bool:
        """Leave a league"""
        # Validate league exists
        liga_validator = LigaValidator()
        liga_validator.validate_exists(db, liga_id)
        
        # Get membership
        membresia = liga_miembro_repository.get_by_liga_usuario(db, liga_id, usuario_id)
        if not membresia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No eres miembro de esta liga"
            )
        
        # Prevent commissioner from leaving
        if membresia.rol.value == "Comisionado":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El comisionado no puede abandonar la liga"
            )
        
        # Get the corresponding fantasy team
        equipo_fantasy = db.query(EquipoFantasyDB).filter(
            EquipoFantasyDB.liga_id == liga_id,
            EquipoFantasyDB.usuario_id == usuario_id
        ).first()
        
        try:
            # Add audit record before deleting
            audit_record = LigaMiembroAudDB(
                liga_id=liga_id,
                usuario_id=usuario_id,
                accion="salir"
            )
            db.add(audit_record)
            
            # Delete fantasy team if it exists
            if equipo_fantasy:
                db.delete(equipo_fantasy)
            
            # Delete membership
            db.delete(membresia)
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error al salir de la liga"
            ) from e
    
    def obtener_miembros_liga(self, db: Session, liga_id: UUID) -> List[LigaMiembroResponse]:
        """Get all members of a league"""
        liga_validator = LigaValidator()
        liga_validator.validate_exists(db, liga_id)
        miembros = liga_miembro_repository.get_miembros_by_liga(db, liga_id)
        return [_to_miembro_response(m) for m in miembros]
    
    def cambiar_alias(self, db: Session, liga_id: UUID, usuario_id: UUID, nuevo_alias: str) -> LigaMiembroResponse:
        """Change user alias in a league"""
        # Validate league exists
        liga_validator = LigaValidator()
        liga_validator.validate_exists(db, liga_id)
        
        # Get membership
        membresia = liga_miembro_repository.get_by_liga_usuario(db, liga_id, usuario_id)
        if not membresia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No eres miembro de esta liga"
            )
        
        # Validate new alias is unique
        liga_validator.validate_alias_unique_in_liga(db, liga_id, nuevo_alias, usuario_id)
        
        # Update alias
        membresia.alias = nuevo_alias
        
        try:
            db.commit()
            db.refresh(membresia)
            return _to_miembro_response(membresia)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error al cambiar el alias"
            ) from e

liga_membresia_service = LigaMembresiaService()