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
    
    def get_by_nombre(self, nombre: str) -> Optional[TemporadaDB]:
        """Get season by name"""
        def query(db: Session):
            return db.query(self.model).filter(self.model.nombre == nombre).first()
        return self._execute_query(query)
    
    def get_actual(self) -> Optional[TemporadaDB]:
        """Get current active season"""
        def query(db: Session):
            return db.query(self.model).filter(self.model.es_actual == True).first()
        return self._execute_query(query)
    
    def get_with_semanas(self, temporada_id: UUID) -> Optional[TemporadaDB]:
        """Get season with its weeks loaded"""
        def query(db: Session):
            return db.query(self.model).options(
                joinedload(self.model.temporadas_semanas)
            ).filter(self.model.id == temporada_id).first()
        return self._execute_query(query)
    
    def get_all_ordered(self) -> List[TemporadaDB]:
        """Get all seasons ordered by creation date"""
        def query(db: Session):
            return db.query(self.model).order_by(self.model.creado_en.desc()).all()
        return self._execute_query(query)
    
    def unset_all_actual(self, exclude_id: Optional[UUID] = None) -> None:
        """Unset es_actual for all seasons except the excluded one"""
        def query(db: Session):
            q = db.query(self.model).filter(self.model.es_actual == True)
            if exclude_id:
                q = q.filter(self.model.id != exclude_id)
            q.update({"es_actual": False})
            db.flush()
        self._execute_query(query)

class TemporadaSemanaRepository(BaseRepository[TemporadaSemanaDB, dict, dict]):
    """Repository for Season Week operations"""
    
    def __init__(self):
        super().__init__(TemporadaSemanaDB)
    
    def get_by_temporada_numero(self, temporada_id: UUID, numero: int) -> Optional[TemporadaSemanaDB]:
        """Get week by season and week number"""
        def query(db: Session):
            return db.query(self.model).filter(
                and_(
                    self.model.temporada_id == temporada_id,
                    self.model.numero == numero
                )
            ).first()
        return self._execute_query(query)
    
    def get_by_temporada(self, temporada_id: UUID) -> List[TemporadaSemanaDB]:
        """Get all weeks for a season ordered by number"""
        def query(db: Session):
            return db.query(self.model).filter(
                self.model.temporada_id == temporada_id
            ).order_by(self.model.numero).all()
        return self._execute_query(query)

# Repository instances
temporada_repository = TemporadaRepository()
temporada_semana_repository = TemporadaSemanaRepository()