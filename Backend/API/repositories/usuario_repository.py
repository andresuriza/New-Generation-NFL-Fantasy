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
    
    def get_by_correo(self, correo: str) -> Optional[UsuarioDB]:
        """Get user by email"""
        def query(db: Session):
            return db.query(self.model).filter(self.model.correo == correo).first()
        return self._execute_query(query)
    
    def get_by_alias(self, alias: str) -> Optional[UsuarioDB]:
        """Get user by alias"""
        def query(db: Session):
            return db.query(self.model).filter(self.model.alias == alias).first()
        return self._execute_query(query)
    
    def get_by_correo_or_alias(self, identifier: str) -> Optional[UsuarioDB]:
        """Get user by email or alias (for login)"""
        def query(db: Session):
            return db.query(self.model).filter(
                or_(
                    self.model.correo == identifier,
                    self.model.alias == identifier
                )
            ).first()
        return self._execute_query(query)
    
    def get_activos(self, skip: int = 0, limit: int = 100) -> List[UsuarioDB]:
        """Get active users only"""
        def query(db: Session):
            return db.query(self.model).filter(
                self.model.estado == "activa"
            ).offset(skip).limit(limit).all()
        return self._execute_query(query)
    
    def get_by_rol(self, rol: str, skip: int = 0, limit: int = 100) -> List[UsuarioDB]:
        """Get users by role"""
        def query(db: Session):
            return db.query(self.model).filter(
                self.model.rol == rol
            ).offset(skip).limit(limit).all()
        return self._execute_query(query)
    
    def search_by_name_or_alias(self, search_term: str, limit: int = 10) -> List[UsuarioDB]:
        """Search users by name or alias (case insensitive)"""
        def query(db: Session):
            search_pattern = f"%{search_term}%"
            return db.query(self.model).filter(
                or_(
                    self.model.nombre.ilike(search_pattern),
                    self.model.alias.ilike(search_pattern)
                )
            ).filter(self.model.estado == "activa").limit(limit).all()
        return self._execute_query(query)
    
    def exists_by_correo(self, correo: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if email exists (excluding specific user ID)"""
        def query(db: Session):
            q = db.query(self.model).filter(self.model.correo == correo)
            if exclude_id:
                q = q.filter(self.model.id != exclude_id)
            return q.first() is not None
        return self._execute_query(query)
    
    def exists_by_alias(self, alias: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if alias exists (excluding specific user ID)"""
        def query(db: Session):
            q = db.query(self.model).filter(self.model.alias == alias)
            if exclude_id:
                q = q.filter(self.model.id != exclude_id)
            return q.first() is not None
        return self._execute_query(query)
    
    def increment_failed_attempts(self, usuario_id: UUID) -> None:
        """Increment failed login attempts"""
        def query(db: Session):
            usuario = db.query(self.model).filter(self.model.id == usuario_id).first()
            if usuario:
                usuario.failed_attempts += 1
                db.flush()
        self._execute_query(query)
    
    def reset_failed_attempts(self, usuario_id: UUID) -> None:
        """Reset failed login attempts to 0"""
        def query(db: Session):
            usuario = db.query(self.model).filter(self.model.id == usuario_id).first()
            if usuario:
                usuario.failed_attempts = 0
                db.flush()
        self._execute_query(query)
    
    def block_user(self, usuario_id: UUID) -> None:
        """Block user account"""
        def query(db: Session):
            usuario = db.query(self.model).filter(self.model.id == usuario_id).first()
            if usuario:
                usuario.estado = "bloqueado"
                db.flush()
        self._execute_query(query)

# Repository instance
usuario_repository = UsuarioRepository()