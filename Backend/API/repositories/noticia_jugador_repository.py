"""
Repository for managing NoticiaJugador (Player News) data access
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload

from repositories.base import BaseRepository
from repositories.db_context import db_context
from models.database_models import NoticiaJugadorDB, UsuarioDB
from models.jugador import NoticiaJugadorCreate


class NoticiaJugadorRepository(BaseRepository[NoticiaJugadorDB, NoticiaJugadorCreate, None]):
    """Repository for player news management"""
    
    def __init__(self):
        super().__init__(NoticiaJugadorDB)
    
    def get_by_jugador_id(self,  jugador_id: UUID, skip: int = 0, limit: int = 100) -> List[NoticiaJugadorDB]:
        """Get all news for a specific player, ordered by creation date (newest first)"""
        return (
            db_context.get_session().query(self.model)
            .filter(self.model.jugador_id == jugador_id)
            .order_by(self.model.creado_en.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_with_author(self, noticia_id: UUID) -> Optional[NoticiaJugadorDB]:
        """Get a news item with author information"""
        return (
            db_context.get_session().query(self.model)
            .options(joinedload(self.model.autor))
            .filter(self.model.id == noticia_id)
            .first()
        )
    
    def get_by_jugador_with_author(self, jugador_id: UUID, skip: int = 0, limit: int = 100) -> List[NoticiaJugadorDB]:
        """Get all news for a player with author information"""
        return (
            db_context.get_session().query(self.model)
            .options(joinedload(self.model.autor))
            .filter(self.model.jugador_id == jugador_id)
            .order_by(self.model.creado_en.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_recent_injury_news(self, days: int = 7, skip: int = 0, limit: int = 100) -> List[NoticiaJugadorDB]:
        """Get recent injury news from the last N days"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return (
            db_context.get_session().query(self.model)
            .options(joinedload(self.model.jugador))
            .filter(
                self.model.es_lesion == True,
                self.model.creado_en >= cutoff_date
            )
            .order_by(self.model.creado_en.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_with_author(self, jugador_id: UUID, obj_in: NoticiaJugadorCreate, author_id: UUID) -> NoticiaJugadorDB:
        """Create a new player news item with author"""
        db_obj_data = obj_in.model_dump()
        
        # Don't convert designation - pass the string value directly to PostgreSQL
        db_obj = self.model(
            jugador_id=jugador_id,
            texto=db_obj_data['texto'],
            es_lesion=db_obj_data['es_lesion'],
            resumen=db_obj_data['resumen'],
            designacion=db_obj_data['designacion'],  # Pass as string
            creado_por=author_id
        )
        with db_context.get_session() as db:
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj


# Create repository instance
noticia_jugador_repository = NoticiaJugadorRepository()