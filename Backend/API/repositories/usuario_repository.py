"""
Repository for Usuario entity operations
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from repositories.base import BaseRepository
from models.database_models import UsuarioDB
from models.usuario import UsuarioCreate, UsuarioUpdate

class UsuarioRepository(BaseRepository[UsuarioDB, UsuarioCreate, UsuarioUpdate]):
    """Repository for User operations"""
    
    def __init__(self):
        super().__init__(UsuarioDB)
    
    def get_by_correo(self, db: Session, correo: str) -> Optional[UsuarioDB]:
        """Get user by email"""
        return db.query(self.model).filter(self.model.correo == correo).first()
    
    def get_by_alias(self, db: Session, alias: str) -> Optional[UsuarioDB]:
        """Get user by alias"""
        return db.query(self.model).filter(self.model.alias == alias).first()
    
    def get_by_correo_or_alias(self, db: Session, identifier: str) -> Optional[UsuarioDB]:
        """Get user by email or alias (for login)"""
        return db.query(self.model).filter(
            or_(
                self.model.correo == identifier,
                self.model.alias == identifier
            )
        ).first()
    
    def get_activos(self, db: Session, skip: int = 0, limit: int = 100) -> List[UsuarioDB]:
        """Get active users only"""
        return db.query(self.model).filter(
            self.model.estado == "activa"
        ).offset(skip).limit(limit).all()
    
    def get_by_rol(self, db: Session, rol: str, skip: int = 0, limit: int = 100) -> List[UsuarioDB]:
        """Get users by role"""
        return db.query(self.model).filter(
            self.model.rol == rol
        ).offset(skip).limit(limit).all()
    
    def search_by_name_or_alias(self, db: Session, search_term: str, limit: int = 10) -> List[UsuarioDB]:
        """Search users by name or alias (case insensitive)"""
        search_pattern = f"%{search_term}%"
        return db.query(self.model).filter(
            or_(
                self.model.nombre.ilike(search_pattern),
                self.model.alias.ilike(search_pattern)
            )
        ).filter(self.model.estado == "activa").limit(limit).all()
    
    def exists_by_correo(self, db: Session, correo: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if email exists (excluding specific user ID)"""
        query = db.query(self.model).filter(self.model.correo == correo)
        if exclude_id:
            query = query.filter(self.model.id != exclude_id)
        return query.first() is not None
    
    def exists_by_alias(self, db: Session, alias: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if alias exists (excluding specific user ID)"""
        query = db.query(self.model).filter(self.model.alias == alias)
        if exclude_id:
            query = query.filter(self.model.id != exclude_id)
        return query.first() is not None
    
    def increment_failed_attempts(self, db: Session, usuario_id: UUID) -> None:
        """Increment failed login attempts"""
        usuario = self.get(db, usuario_id)
        if usuario:
            usuario.failed_attempts += 1
            db.commit()
    
    def reset_failed_attempts(self, db: Session, usuario_id: UUID) -> None:
        """Reset failed login attempts to 0"""
        usuario = self.get(db, usuario_id)
        if usuario:
            usuario.failed_attempts = 0
            db.commit()
    
    def block_user(self, db: Session, usuario_id: UUID) -> None:
        """Block user account"""
        usuario = self.get(db, usuario_id)
        if usuario:
            usuario.estado = "bloqueado"
            db.commit()

# Repository instance
usuario_repository = UsuarioRepository()