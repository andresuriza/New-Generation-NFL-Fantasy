"""
Repository for Liga entity operations
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from repositories.base import BaseRepository
from models.database_models import LigaDB, LigaMiembroDB, LigaCuposVistaDB, LigaCupoDB
from models.liga import LigaCreate, LigaUpdate

class LigaRepository(BaseRepository[LigaDB, LigaCreate, LigaUpdate]):
    """Repository for League operations"""
    
    def __init__(self):
        super().__init__(LigaDB)
    
    def get_by_nombre(self, db: Session, nombre: str) -> Optional[LigaDB]:
        """Get league by name"""
        return db.query(self.model).filter(self.model.nombre == nombre).first()
    
    def get_with_miembros(self, db: Session, liga_id: UUID) -> Optional[LigaDB]:
        """Get league with its members loaded"""
        return db.query(self.model).options(
            joinedload(self.model.miembros)
        ).filter(self.model.id == liga_id).first()
    
    def get_ligas_disponibles(self, db: Session) -> List[LigaCuposVistaDB]:
        """Get leagues with available spots"""
        return db.query(LigaCuposVistaDB).filter(
            LigaCuposVistaDB.cupos_disponibles > 0
        ).all()
    
    def has_associated_ligas(self, db: Session, temporada_id: UUID) -> bool:
        """Check if a season has associated leagues"""
        return db.query(self.model).filter(self.model.temporada_id == temporada_id).count() > 0

class LigaMiembroRepository(BaseRepository[LigaMiembroDB, dict, dict]):
    """Repository for League Member operations"""
    
    def __init__(self):
        super().__init__(LigaMiembroDB)
    
    def get_by_liga_usuario(self, db: Session, liga_id: UUID, usuario_id: UUID) -> Optional[LigaMiembroDB]:
        """Get membership by league and user"""
        return db.query(self.model).filter(
            and_(
                self.model.liga_id == liga_id,
                self.model.usuario_id == usuario_id
            )
        ).first()
    
    def get_by_liga_alias(self, db: Session, liga_id: UUID, alias: str) -> Optional[LigaMiembroDB]:
        """Get membership by league and alias"""
        return db.query(self.model).filter(
            and_(
                self.model.liga_id == liga_id,
                self.model.alias == alias
            )
        ).first()
    
    def get_miembros_by_liga(self, db: Session, liga_id: UUID) -> List[LigaMiembroDB]:
        """Get all members of a league"""
        return db.query(self.model).filter(self.model.liga_id == liga_id).all()

class LigaCupoRepository(BaseRepository[LigaCupoDB, dict, dict]):
    """Repository for League Quota operations"""
    
    def __init__(self):
        super().__init__(LigaCupoDB)
    
    def get_by_liga(self, db: Session, liga_id: UUID) -> Optional[LigaCupoDB]:
        """Get quota info for a league"""
        return db.query(self.model).filter(self.model.liga_id == liga_id).first()

# Repository instances
liga_repository = LigaRepository()
liga_miembro_repository = LigaMiembroRepository()
liga_cupo_repository = LigaCupoRepository()