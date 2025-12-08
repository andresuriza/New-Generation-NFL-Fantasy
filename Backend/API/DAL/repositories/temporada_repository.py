"""
Repository for Temporada entity operations
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from datetime import date

from DAL.repositories.base import BaseRepository
from models.database_models import TemporadaDB, TemporadaSemanaDB
from models.temporada import TemporadaCreate, TemporadaUpdate

class TemporadaRepository(BaseRepository[TemporadaDB, TemporadaCreate, TemporadaUpdate]):
    """Repository for Season operations"""
    
    def __init__(self):
        super().__init__(TemporadaDB)
    
    def get_by_nombre(self, nombre: str, exclude_id: Optional[UUID] = None) -> Optional[TemporadaDB]:
        """Get season by name"""
        def query(db: Session):
            q = db.query(self.model).filter(self.model.nombre == nombre)
            if exclude_id:
                q = q.filter(self.model.id != exclude_id)
            return q.first()
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
    def get_overlapping_season(self, fecha_inicio: date, fecha_fin: date, exclude_id: Optional[UUID] = None) -> Optional[TemporadaDB]:
        """Get season that overlaps with given date range"""
        def query(db: Session):
            q = db.query(self.model).filter(
                and_(
                    self.model.fecha_inicio <= fecha_fin,
                    self.model.fecha_fin >= fecha_inicio
                )
            )
            if exclude_id:
                q = q.filter(self.model.id != exclude_id)
            return q.first()
        return self._execute_query(query)
    def count_ligas_by_temporada(self, temporada_id: UUID) -> int:
        """Count leagues using this season"""
        from models.database_models import LigaDB
    
        def query(db: Session):
            return db.query(LigaDB).filter(LigaDB.temporada_id == temporada_id).count()
        return self._execute_query(query)
    
    def has_associated_ligas(self, temporada_id: UUID) -> bool:
        """Check if season has associated leagues"""
        from models.database_models import LigaDB
        
        def query(db: Session):
            count = db.query(LigaDB).filter(LigaDB.temporada_id == temporada_id).count()
            return count > 0
        return self._execute_query(query)

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

    def get_week_by_numero(self, temporada_id: UUID, numero: int) -> Optional[TemporadaSemanaDB]:
        """Get week by number in a season"""
        from models.database_models import TemporadaSemanaDB

        def query(db: Session):
            return db.query(TemporadaSemanaDB).filter(
                and_(
                    TemporadaSemanaDB.temporada_id == temporada_id,
                    TemporadaSemanaDB.numero == numero
                )
            ).first()
        return self._execute_query(query)

    def get_overlapping_week(self, temporada_id: UUID, fecha_inicio: date, fecha_fin: date, exclude_numero: Optional[int] = None) -> Optional[TemporadaSemanaDB]:
        """Get week that overlaps with the given date range in a season"""
        from models.database_models import TemporadaSemanaDB

        def query(db: Session):
            q = db.query(TemporadaSemanaDB).filter(
                and_(
                    TemporadaSemanaDB.temporada_id == temporada_id,
                    TemporadaSemanaDB.fecha_inicio < fecha_fin,
                    TemporadaSemanaDB.fecha_fin > fecha_inicio
                )
            )
            if exclude_numero:
                q = q.filter(TemporadaSemanaDB.numero != exclude_numero)
            return q.first()
        return self._execute_query(query)

    def create_from_pydantic(self, semana_create) -> TemporadaSemanaDB:
        """Create a week from a Pydantic model"""
        def query(db: Session):
            nueva_semana = TemporadaSemanaDB(**semana_create.model_dump())
            db.add(nueva_semana)
            db.flush()
            db.refresh(nueva_semana)
            return nueva_semana
        return self._execute_query(query)

# Repository instances
temporada_repository = TemporadaRepository()
temporada_semana_repository = TemporadaSemanaRepository()