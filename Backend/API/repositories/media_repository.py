"""
Repository for Media entity operations
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload

from repositories.base import BaseRepository
from models.database_models import MediaDB
from models.media import MediaCreate, MediaUpdate

class MediaRepository(BaseRepository[MediaDB, MediaCreate, MediaUpdate]):
    """Repository for Media operations"""
    
    def __init__(self):
        super().__init__(MediaDB)
    
    def get_by_equipo(self, equipo_id: UUID) -> Optional[MediaDB]:
        """Get media by team ID"""
        def query(db:Session):
            db.query(self.model).filter(self.model.equipo_id == equipo_id).first()
        return self._execute_query(query)
    
    def get_with_equipo(self, equipo_id: UUID) -> Optional[MediaDB]:
        """Get media with team information loaded"""
        def query(db: Session):
            return db.query(self.model).options(
                joinedload(self.model.equipo)
            ).filter(self.model.equipo_id == equipo_id).first()
        return self._execute_query(query)
    
    def delete_by_equipo(self, equipo_id: UUID) -> bool:
        """Delete media by team ID"""
        def query(db: Session):
            media = db.query(get_by_equipo(equipo_id))
            if media:
                try:
                    db.delete(media)
                    db.commit()
                    return True
                except Exception:
                    db.rollback()
                    return False
            return False
        return self._execute_query(query)
    
    def exists_for_equipo(self, equipo_id: UUID) -> bool:
        """Check if media exists for a team"""
        def query(db: Session):
            return db.query(MediaDB).filter(MediaDB.equipo_id == equipo_id).first() is not None
        return self._execute_query(query)
    
    def update(self, media: MediaDB, media_update) -> MediaDB:
        """Update media"""
        def query(db: Session):

            for field, value in media_update.dict(exclude_unset=True).items():
                setattr(media, field, value)
            db.commit()
            db.refresh(media)
            return media
        return self._execute_query(query)
    
    def delete_by_equipo(self, equipo_id: UUID) -> bool:
        """Delete media for a team"""
        def query(db: Session):
            
            media = self.get_by_equipo(db, equipo_id)
            if media:
                db.delete(media)
                db.commit()
                return True
            return False
        return self._execute_query(query)
    
    def get_recent_media(self, limit: int = 10) -> List[MediaDB]:
        """Get recently created media"""
        def query(db: Session):
            return db.query(self.model).order_by(
                self.model.creado_en.desc()
            ).limit(limit).all()
        return self._execute_query(query)
    
    def get_by_url_pattern(self, url_pattern: str) -> List[MediaDB]:
        """Get media by URL pattern (for cleanup or validation)"""
        def query(db: Session):
            return db.query(self.model).filter(
                self.model.url.like(f"%{url_pattern}%")
            ).all()
        return self._execute_query(query)
# Repository instance
media_repository = MediaRepository()