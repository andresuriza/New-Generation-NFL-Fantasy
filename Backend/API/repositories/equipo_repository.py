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
    
    def get_by_nombre(self, nombre: str) -> Optional[EquipoDB]:
        """Get NFL team by name (case-insensitive)"""
        def query(db: Session):
            return db.query(EquipoDB).filter(
                func.lower(EquipoDB.nombre) == func.lower(nombre)
            ).first()
        return self._execute_query(query)
    
    def get_with_media(self, equipo_id: UUID) -> Optional[EquipoDB]:
        """Get NFL team with media loaded"""
        def query(db: Session):
            return db.query(self.model).options(
                joinedload(self.model.media)
            ).filter(self.model.id == equipo_id).first()
        return self._execute_query(query)


# Create repository instance
equipo_repository = EquipoNFLRepository()
