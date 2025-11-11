"""
Repository for Jugadores (Players) entity operations
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func

from repositories.base import BaseRepository
from models.database_models import JugadoresDB, PosicionJugadorEnum
from models.jugador import JugadorCreate, JugadorUpdate, JugadorFilter

class JugadorRepository(BaseRepository[JugadoresDB, JugadorCreate, JugadorUpdate]):
    """Repository for Player operations"""
    
    def __init__(self):
        super().__init__(JugadoresDB)
    
    def get_by_nombre_equipo(self, db: Session, nombre: str, equipo_id: UUID) -> Optional[JugadoresDB]:
        """Get player by name and NFL team"""
        return db.query(self.model).filter(
            and_(
                self.model.nombre == nombre,
                self.model.equipo_id == equipo_id
            )
        ).first()
    
    def get_with_equipo(self, db: Session, jugador_id: UUID) -> Optional[JugadoresDB]:
        """Get player with NFL team information loaded"""
        return db.query(self.model).options(
            joinedload(self.model.equipo_nfl)
        ).filter(self.model.id == jugador_id).first()
    
    def get_by_equipo(self, db: Session, equipo_id: UUID, skip: int = 0, limit: int = 100) -> List[JugadoresDB]:
        """Get all players from a specific NFL team"""
        return db.query(self.model).filter(
            self.model.equipo_id == equipo_id
        ).offset(skip).limit(limit).all()
    
    def get_by_posicion(self, db: Session, posicion: PosicionJugadorEnum, skip: int = 0, limit: int = 100) -> List[JugadoresDB]:
        """Get all players by position"""
        return db.query(self.model).filter(
            self.model.posicion == posicion
        ).offset(skip).limit(limit).all()
    
    def get_activos(self, db: Session, skip: int = 0, limit: int = 100) -> List[JugadoresDB]:
        """Get all active players"""
        return db.query(self.model).filter(
            self.model.activo == True
        ).offset(skip).limit(limit).all()
    
    def search_by_nombre(self, db: Session, nombre: str, skip: int = 0, limit: int = 100) -> List[JugadoresDB]:
        """Search players by name (case insensitive partial match)"""
        return db.query(self.model).filter(
            func.lower(self.model.nombre).contains(func.lower(nombre))
        ).offset(skip).limit(limit).all()
    
    def get_with_filters(self, db: Session, filters: JugadorFilter, skip: int = 0, limit: int = 100) -> List[JugadoresDB]:
        """Get players with multiple filters"""
        query = db.query(self.model)
        
        if filters.posicion:
            query = query.filter(self.model.posicion == filters.posicion)
        
        if filters.equipo_id:
            query = query.filter(self.model.equipo_id == filters.equipo_id)
        
        if filters.activo is not None:
            query = query.filter(self.model.activo == filters.activo)
        
        if filters.nombre:
            query = query.filter(
                func.lower(self.model.nombre).contains(func.lower(filters.nombre))
            )
        
        return query.offset(skip).limit(limit).all()
    
    def count_by_equipo(self, db: Session, equipo_id: UUID) -> int:
        """Count players in a specific NFL team"""
        return db.query(self.model).filter(self.model.equipo_id == equipo_id).count()
    
    def count_by_posicion(self, db: Session, posicion: PosicionJugadorEnum) -> int:
        """Count players by position"""
        return db.query(self.model).filter(self.model.posicion == posicion).count()
    
    def get_by_liga_id(self, db: Session, liga_id: UUID, skip: int = 0, limit: int = 100) -> List[JugadoresDB]:
        """Get all players from teams in a specific league"""
        from models.database_models import EquipoDB
        return db.query(self.model).join(
            EquipoDB, self.model.equipo_id == EquipoDB.id
        ).filter(
            EquipoDB.liga_id == liga_id
        ).offset(skip).limit(limit).all()
    
    def get_by_usuario_id(self, db: Session, usuario_id: UUID, skip: int = 0, limit: int = 100) -> List[JugadoresDB]:
        """Get all players from teams owned by a specific user"""
        from models.database_models import EquipoDB
        return db.query(self.model).join(
            EquipoDB, self.model.equipo_id == EquipoDB.id
        ).filter(
            EquipoDB.usuario_id == usuario_id
        ).offset(skip).limit(limit).all()

# Repository instance
jugador_repository = JugadorRepository()