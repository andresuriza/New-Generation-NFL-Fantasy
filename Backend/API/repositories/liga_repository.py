"""
Repository for Liga entity operations
"""
from typing import List, Optional, TYPE_CHECKING
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from repositories.base import BaseRepository
from models.database_models import LigaDB, LigaMiembroDB, LigaCupoDB
from models.liga import LigaCreate, LigaUpdate

if TYPE_CHECKING:
    from models.liga import LigaFilter

class LigaRepository(BaseRepository[LigaDB, LigaCreate, LigaUpdate]):
    """Repository for League operations"""
    
    def __init__(self):
        super().__init__(LigaDB)
    
    def get_by_nombre(self, nombre: str) -> Optional[LigaDB]:
        """Get league by name"""
        def query(db: Session):
            return db.query(self.model).filter(self.model.nombre == nombre).first()
        return self._execute_query(query)
    
    def get_with_miembros(self, liga_id: UUID) -> Optional[LigaDB]:
        """Get league with its members loaded"""
        def query(db: Session):
            return db.query(self.model).options(
                joinedload(self.model.miembros)
            ).filter(self.model.id == liga_id).first()
        return self._execute_query(query)
    
    def search_with_filter(self, filtros: 'LigaFilter', skip: int = 0, limit: int = 100) -> List[LigaDB]:
        """Search leagues with filters"""
        def query(db: Session):
            q = db.query(self.model)
            
            if filtros.nombre:
                q = q.filter(self.model.nombre.ilike(f"%{filtros.nombre}%"))
            
            if filtros.temporada_id:
                q = q.filter(self.model.temporada_id == filtros.temporada_id)
            
            if filtros.estado:
                q = q.filter(self.model.estado == filtros.estado)
            
            return q.offset(skip).limit(limit).all()
        return self._execute_query(query)
    
    def has_associated_ligas(self, temporada_id: UUID) -> bool:
        """Check if a season has associated leagues"""
        def query(db: Session):
            return db.query(self.model).filter(self.model.temporada_id == temporada_id).count() > 0
        return self._execute_query(query)
    def is_usuario_miembro(self, usuario_id: UUID, liga_id: UUID) -> bool:
        """Check if a user is a member of a league"""
        def query(db: Session):
            from models.database_models import LigaMiembroDB
            return db.query(LigaMiembroDB).filter(
                and_(
                    LigaMiembroDB.usuario_id == usuario_id,
                    LigaMiembroDB.liga_id == liga_id
                )
            ).count() > 0
        return self._execute_query(query)

class LigaMiembroRepository(BaseRepository[LigaMiembroDB, dict, dict]):
    """Repository for League Member operations"""
    
    def __init__(self):
        super().__init__(LigaMiembroDB)
    
    def get_by_liga_usuario(self, liga_id: UUID, usuario_id: UUID) -> Optional[LigaMiembroDB]:
        """Get membership by league and user"""
        def query(db: Session):
            return db.query(self.model).filter(
                and_(
                    self.model.liga_id == liga_id,
                    self.model.usuario_id == usuario_id
                )
            ).first()
        return self._execute_query(query)
    
    def get_by_liga_alias(self, liga_id: UUID, alias: str) -> Optional[LigaMiembroDB]:
        """Get membership by league and alias"""
        def query(db: Session):
            return db.query(self.model).filter(
                and_(
                    self.model.liga_id == liga_id,
                    self.model.alias == alias
                )
            ).first()
        return self._execute_query(query)
    
    def get_miembros_by_liga(self, liga_id: UUID) -> List[LigaMiembroDB]:
        """Get all members of a league"""
        def query(db: Session):
            return db.query(self.model).filter(self.model.liga_id == liga_id).all()
        return self._execute_query(query)
    
    def count_miembros_by_liga(self, liga_id: UUID) -> int:
        """Count members in a league (excluding comisionado)"""
        def query(db: Session):
            from models.database_models import RolMembresiaEnum
            return db.query(self.model).filter(
                and_(
                    self.model.liga_id == liga_id,
                    self.model.rol == RolMembresiaEnum.Manager
                )
            ).count()
        return self._execute_query(query)

class LigaCupoRepository(BaseRepository[LigaCupoDB, dict, dict]):
    """Repository for League Quota operations"""
    
    def __init__(self):
        super().__init__(LigaCupoDB)
    
    def get_by_liga(self, liga_id: UUID) -> Optional[LigaCupoDB]:
        """Get quota info for a league"""
        def query(db: Session):
            return db.query(self.model).filter(self.model.liga_id == liga_id).first()
        return self._execute_query(query)

# Repository instances
liga_repository = LigaRepository()
liga_miembro_repository = LigaMiembroRepository()
liga_cupo_repository = LigaCupoRepository()