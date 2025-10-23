"""
Repository for Equipo entity operations
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from repositories.base import BaseRepository
from models.database_models import EquipoDB, MediaDB
from models.equipo import EquipoCreate, EquipoUpdate

class EquipoRepository(BaseRepository[EquipoDB, EquipoCreate, EquipoUpdate]):
    """Repository for Team operations"""
    
    def __init__(self):
        super().__init__(EquipoDB)
    
    def get_by_liga_usuario(self, db: Session, liga_id: UUID, usuario_id: UUID) -> Optional[EquipoDB]:
        """Get team by league and user"""
        return db.query(self.model).filter(
            and_(
                self.model.liga_id == liga_id,
                self.model.usuario_id == usuario_id
            )
        ).first()
    
    def get_by_liga_nombre(self, db: Session, liga_id: UUID, nombre: str) -> Optional[EquipoDB]:
        """Get team by league and name (case insensitive)"""
        return db.query(self.model).filter(
            and_(
                self.model.liga_id == liga_id,
                self.model.nombre.ilike(nombre)
            )
        ).first()
    
    def get_with_media(self, db: Session, equipo_id: UUID) -> Optional[EquipoDB]:
        """Get team with media loaded"""
        return db.query(self.model).options(
            joinedload(self.model.media)
        ).filter(self.model.id == equipo_id).first()
    
    def get_by_liga(self, db: Session, liga_id: UUID) -> List[EquipoDB]:
        """Get all teams in a league"""
        return db.query(self.model).filter(self.model.liga_id == liga_id).all()
    
    def get_by_usuario(self, db: Session, usuario_id: UUID) -> List[EquipoDB]:
        """Get all teams owned by a user"""
        return db.query(self.model).filter(self.model.usuario_id == usuario_id).all()

# Repository instance
equipo_repository = EquipoRepository()