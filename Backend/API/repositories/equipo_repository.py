"""
Repository for NFL Equipo entity operations
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from repositories.base import BaseRepository
from models.database_models import EquipoDB, MediaDB
from models.equipo import EquipoNFLCreate, EquipoNFLUpdate

class EquipoNFLRepository(BaseRepository[EquipoDB, EquipoNFLCreate, EquipoNFLUpdate]):
    """Repository for NFL Team operations"""
    
    def __init__(self):
        super().__init__(EquipoDB)
    
    def get_by_nombre(self, db: Session, nombre: str) -> Optional[EquipoDB]:
        """Get NFL team by name (case-insensitive)"""
        return db.query(EquipoDB).filter(
            func.lower(EquipoDB.nombre) == func.lower(nombre)
        ).first()
    
    def get_with_media(self, db: Session, equipo_id: UUID) -> Optional[EquipoDB]:
        """Get NFL team with media loaded"""
        return db.query(self.model).options(
            joinedload(self.model.media)
        ).filter(self.model.id == equipo_id).first()


# Create repository instance
equipo_repository = EquipoNFLRepository()
