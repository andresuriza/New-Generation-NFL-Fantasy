"""
Repository for Temporada entity operations
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from repositories.base import BaseRepository
from models.database_models import TemporadaDB, TemporadaSemanaDB
from models.temporada import TemporadaCreate, TemporadaUpdate

class TemporadaRepository(BaseRepository[TemporadaDB, TemporadaCreate, TemporadaUpdate]):
    """Repository for Season operations"""
    
    def __init__(self):
        super().__init__(TemporadaDB)
    
    def get_by_nombre(self, db: Session, nombre: str) -> Optional[TemporadaDB]:
        """Get season by name"""
        return db.query(self.model).filter(self.model.nombre == nombre).first()
    
    def get_actual(self, db: Session) -> Optional[TemporadaDB]:
        """Get current active season"""
        return db.query(self.model).filter(self.model.es_actual == True).first()
    
    def get_with_semanas(self, db: Session, temporada_id: UUID) -> Optional[TemporadaDB]:
        """Get season with its weeks loaded"""
        return db.query(self.model).options(
            joinedload(self.model.temporadas_semanas)
        ).filter(self.model.id == temporada_id).first()
    
    def get_all_ordered(self, db: Session) -> List[TemporadaDB]:
        """Get all seasons ordered by creation date"""
        return db.query(self.model).order_by(self.model.creado_en.desc()).all()
    
    def unset_all_actual(self, db: Session, exclude_id: Optional[UUID] = None) -> None:
        """Unset es_actual for all seasons except the excluded one"""
        query = db.query(self.model).filter(self.model.es_actual == True)
        if exclude_id:
            query = query.filter(self.model.id != exclude_id)
        query.update({"es_actual": False})

class TemporadaSemanaRepository(BaseRepository[TemporadaSemanaDB, dict, dict]):
    """Repository for Season Week operations"""
    
    def __init__(self):
        super().__init__(TemporadaSemanaDB)
    
    def get_by_temporada_numero(self, db: Session, temporada_id: UUID, numero: int) -> Optional[TemporadaSemanaDB]:
        """Get week by season and week number"""
        return db.query(self.model).filter(
            and_(
                self.model.temporada_id == temporada_id,
                self.model.numero == numero
            )
        ).first()
    
    def get_by_temporada(self, db: Session, temporada_id: UUID) -> List[TemporadaSemanaDB]:
        """Get all weeks for a season ordered by number"""
        return db.query(self.model).filter(
            self.model.temporada_id == temporada_id
        ).order_by(self.model.numero).all()

# Repository instances
temporada_repository = TemporadaRepository()
temporada_semana_repository = TemporadaSemanaRepository()