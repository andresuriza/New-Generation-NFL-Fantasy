"""
Repository for Equipos Fantasy (Fantasy Teams) data access operations
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_, func

from models.database_models import EquipoFantasyDB, EquipoFantasyAuditDB
from models.equipo_fantasy import EquipoFantasyCreate, EquipoFantasyUpdate, EquipoFantasyFilter
from repositories.base import BaseRepository

class EquipoFantasyRepository(BaseRepository[EquipoFantasyDB, EquipoFantasyCreate, EquipoFantasyUpdate]):
    
    def __init__(self):
        super().__init__(EquipoFantasyDB)
    
    def get_by_liga_and_nombre(self,  liga_id: UUID, nombre: str) -> Optional[EquipoFantasyDB]:
        """Get fantasy team by league ID and name"""
        return db_context.get_session().query(EquipoFantasyDB).filter(
            and_(
                EquipoFantasyDB.liga_id == liga_id,
                func.lower(EquipoFantasyDB.nombre) == func.lower(nombre)
            )
        ).first()
    
    def get_by_liga_and_usuario(self,  liga_id: UUID, usuario_id: UUID) -> Optional[EquipoFantasyDB]:
        """Get fantasy team by league ID and user ID"""
        return db_context.get_session().query(EquipoFantasyDB).filter(
            and_(
                EquipoFantasyDB.liga_id == liga_id,
                EquipoFantasyDB.usuario_id == usuario_id
            )
        ).first()
    
    def get_with_relations(self, equipo_id: UUID) -> Optional[EquipoFantasyDB]:
        """Get fantasy team with league and user relationships loaded"""
        return db_context.get_session().query(EquipoFantasyDB).options(
            selectinload(EquipoFantasyDB.liga),
            selectinload(EquipoFantasyDB.usuario)
        ).filter(EquipoFantasyDB.id == equipo_id).first()
    
    def get_by_liga(self, liga_id: UUID, skip: int = 0, limit: int = 100) -> List[EquipoFantasyDB]:
        """Get all fantasy teams in a league"""
        return db_context.get_session().query(EquipoFantasyDB).filter(
            EquipoFantasyDB.liga_id == liga_id
        ).offset(skip).limit(limit).all()
    
    def get_by_usuario(self, usuario_id: UUID, skip: int = 0, limit: int = 100) -> List[EquipoFantasyDB]:
        """Get all fantasy teams owned by a user"""
        return db_context.get_session().query(EquipoFantasyDB).filter(
            EquipoFantasyDB.usuario_id == usuario_id
        ).offset(skip).limit(limit).all()
    
    def search_with_filter(self, filtros: EquipoFantasyFilter, skip: int = 0, limit: int = 100) -> List[EquipoFantasyDB]:
        """Search fantasy teams with filters"""
        query = db_context.get_session().query(EquipoFantasyDB)
        
        if filtros.liga_id:
            query = query.filter(EquipoFantasyDB.liga_id == filtros.liga_id)
        
        if filtros.usuario_id:
            query = query.filter(EquipoFantasyDB.usuario_id == filtros.usuario_id)
        
        if filtros.nombre:
            search_term = f"%{filtros.nombre.lower()}%"
            query = query.filter(func.lower(EquipoFantasyDB.nombre).like(search_term))
        
        return query.offset(skip).limit(limit).all()
    
    def count_by_liga(self,  liga_id: UUID) -> int:
        """Count fantasy teams in a league"""
        return db_context.get_session().query(EquipoFantasyDB).filter(
            EquipoFantasyDB.liga_id == liga_id
        ).count()
    
    def exists_nombre_in_liga(self, liga_id: UUID, nombre: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if team name exists in league (excluding optionally provided ID)"""
        query = db_context.get_session().query(EquipoFantasyDB).filter(
            and_(
                EquipoFantasyDB.liga_id == liga_id,
                func.lower(EquipoFantasyDB.nombre) == func.lower(nombre)
            )
        )
        
        if exclude_id:
            query = query.filter(EquipoFantasyDB.id != exclude_id)
        
        return query.first() is not None
    def get_by_usuario_and_liga(self, usuario_id: UUID, liga_id: UUID, exclude_id: Optional[UUID] = None) -> Optional[EquipoFantasyDB]:
        """Get fantasy team by user ID and league ID"""
        query = db_context.get_session().query(EquipoFantasyDB).filter(
            and_(
                EquipoFantasyDB.usuario_id == usuario_id,
                EquipoFantasyDB.liga_id == liga_id
            )
        )
        
        if exclude_id:
            query = query.filter(EquipoFantasyDB.id != exclude_id)
        
        return query.first()
class EquipoFantasyAuditRepository:
    
    def __init__(self):
        self.model = EquipoFantasyAuditDB
    
    def get_by_equipo_fantasy(self, equipo_fantasy_id: UUID, skip: int = 0, limit: int = 100) -> List[EquipoFantasyAuditDB]:
        """Get audit logs for a fantasy team"""
        return db_context.get_session().query(EquipoFantasyAuditDB).options(
            selectinload(EquipoFantasyAuditDB.usuario)
        ).filter(
            EquipoFantasyAuditDB.equipo_fantasy_id == equipo_fantasy_id
        ).order_by(EquipoFantasyAuditDB.timestamp_accion.desc()).offset(skip).limit(limit).all()
    
    def get_recent_changes(self, liga_id: UUID, limit: int = 50) -> List[EquipoFantasyAuditDB]:
        """Get recent audit changes for all fantasy teams in a league"""
        return db_context.get_session().query(EquipoFantasyAuditDB).join(EquipoFantasyDB).options(
            selectinload(EquipoFantasyAuditDB.usuario),
            selectinload(EquipoFantasyAuditDB.equipo_fantasy)
        ).filter(
            EquipoFantasyDB.liga_id == liga_id
        ).order_by(EquipoFantasyAuditDB.timestamp_accion.desc()).limit(limit).all()

# Repository instances
equipo_fantasy_repository = EquipoFantasyRepository()
equipo_fantasy_audit_repository = EquipoFantasyAuditRepository()