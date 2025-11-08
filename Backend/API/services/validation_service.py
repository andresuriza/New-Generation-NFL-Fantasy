"""
Validation service for business rules
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.database_models import LigaDB, TemporadaDB, UsuarioDB, LigaMiembroDB, LigaCupoDB
#TODO: VERIFICACION DE SEMANAS DE TEMPORADA
#TODO: Separacion de http de servicios
class ValidationService:
    """Service for handling business rule validations"""
    
    @staticmethod
    def validate_temporada_exists(db: Session, temporada_id: UUID) -> TemporadaDB:
        """Validate that a season exists"""
        temporada = db.query(TemporadaDB).filter(TemporadaDB.id == temporada_id).first()
        if not temporada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Temporada no encontrada"
            )
        return temporada
    
    @staticmethod
    def validate_usuario_exists(db: Session, usuario_id: UUID) -> UsuarioDB:
        """Validate that a user exists"""
        usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return usuario
    
    @staticmethod
    def validate_liga_exists(db: Session, liga_id: UUID) -> LigaDB:
        """Validate that a league exists"""
        liga = db.query(LigaDB).filter(LigaDB.id == liga_id).first()
        if not liga:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Liga no encontrada"
            )
        return liga
    
    @staticmethod
    def validate_liga_nombre_unique(db: Session, nombre: str, exclude_id: Optional[UUID] = None) -> None:
        """Validate that a league name is unique"""
        query = db.query(LigaDB).filter(LigaDB.nombre == nombre)
        if exclude_id:
            query = query.filter(LigaDB.id != exclude_id)
        
        if query.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una liga con ese nombre"
            )
    
    @staticmethod
    def validate_liga_editable(liga: LigaDB) -> None:
        """Validate that a league can be edited (only in Pre_draft state)"""
        if liga.estado.value != "Pre_draft":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden modificar ligas en estado Pre_draft"
            )
    
    @staticmethod
    def validate_liga_has_cupos(db: Session, liga_id: UUID) -> None:
        """Validate that a league has available spots"""
        from repositories.liga_repository import liga_repository, liga_miembro_repository
        
        # Get the league to check equipos_max
        liga = liga_repository.get(db, liga_id)
        if not liga:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Liga no encontrada"
            )
        
        # Count current members in the league (excluding comisionado)
        current_members_count = liga_miembro_repository.count_miembros_by_liga(db, liga_id)
        
        # Check if league is full (use equipos_max as the limit, comisionado doesn't count)
        if current_members_count >= liga.equipos_max:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La liga está llena"
            )
    
    @staticmethod
    def get_liga_current_members_count(db: Session, liga_id: UUID) -> int:
        """Get the current number of members in a league"""
        from repositories.liga_repository import liga_miembro_repository
        return liga_miembro_repository.count_miembros_by_liga(db, liga_id)
    
    @staticmethod
    def validate_usuario_not_in_liga(db: Session, liga_id: UUID, usuario_id: UUID) -> None:
        """Validate that a user is not already in the league"""
        miembro_existente = db.query(LigaMiembroDB).filter(
            LigaMiembroDB.liga_id == liga_id,
            LigaMiembroDB.usuario_id == usuario_id
        ).first()
        
        if miembro_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya eres miembro de esta liga"
            )
    
    @staticmethod
    def validate_alias_unique_in_liga(db: Session, liga_id: UUID, alias: str, exclude_usuario_id: Optional[UUID] = None) -> None:
        """Validate that an alias is unique within a league"""
        query = db.query(LigaMiembroDB).filter(
            LigaMiembroDB.liga_id == liga_id,
            LigaMiembroDB.alias == alias
        )
        
        if exclude_usuario_id:
            query = query.filter(LigaMiembroDB.usuario_id != exclude_usuario_id)
        
        if query.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ese alias ya está ocupado en esta liga"
            )

validation_service = ValidationService()