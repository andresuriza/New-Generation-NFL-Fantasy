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
    
    def get_by_equipo(self, db: Session, equipo_id: UUID) -> Optional[MediaDB]:
        """Get media by team ID"""
        return db.query(self.model).filter(self.model.equipo_id == equipo_id).first()
    
    def get_with_equipo(self, db: Session, equipo_id: UUID) -> Optional[MediaDB]:
        """Get media with team information loaded"""
        return db.query(self.model).options(
            joinedload(self.model.equipo)
        ).filter(self.model.equipo_id == equipo_id).first()
    
    def delete_by_equipo(self, db: Session, equipo_id: UUID) -> bool:
        """Delete media by team ID"""
        media = self.get_by_equipo(db, equipo_id)
        if media:
            try:
                db.delete(media)
                db.commit()
                return True
            except Exception:
                db.rollback()
                return False
        return False
    
    def exists_for_equipo(self, db: Session, equipo_id: UUID) -> bool:
        """Check if media exists for a team"""
        return db.query(MediaDB).filter(MediaDB.equipo_id == equipo_id).first() is not None
    
    def update(self, db: Session, media: MediaDB, media_update) -> MediaDB:
        """Update media"""
        for field, value in media_update.dict(exclude_unset=True).items():
            setattr(media, field, value)
        db.commit()
        db.refresh(media)
        return media
    
    def delete_by_equipo(self, db: Session, equipo_id: UUID) -> bool:
        """Delete media for a team"""
        media = self.get_by_equipo(db, equipo_id)
        if media:
            db.delete(media)
            db.commit()
            return True
        return False
    
    def get_recent_media(self, db: Session, limit: int = 10) -> List[MediaDB]:
        """Get recently created media"""
        return db.query(self.model).order_by(
            self.model.creado_en.desc()
        ).limit(limit).all()
    
    def get_by_url_pattern(self, db: Session, url_pattern: str) -> List[MediaDB]:
        """Get media by URL pattern (for cleanup or validation)"""
        return db.query(self.model).filter(
            self.model.url.like(f"%{url_pattern}%")
        ).all()

# Repository instance
media_repository = MediaRepository()