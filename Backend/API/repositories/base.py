"""
Base repository pattern implementation for consistent data access
Repositories manage their own database sessions internally
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Type, TypeVar, Generic, Callable, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from contextlib import contextmanager

from repositories.db_context import db_context

# Generic types
ModelType = TypeVar('ModelType')
CreateSchemaType = TypeVar('CreateSchemaType')
UpdateSchemaType = TypeVar('UpdateSchemaType')

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    """Base repository class with common CRUD operations
    
    All database operations are handled internally by the repository.
    No external code needs to manage database sessions.
    """
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def _execute_query(self, query_func: Callable[[Session], Any]) -> Any:
        """Execute a query function with automatic session management"""
        with db_context.get_session() as db:
            return query_func(db)
    
    def get(self, id: UUID) -> Optional[ModelType]:
        """Get a single record by ID"""
        def query(db: Session):
            return db.query(self.model).filter(self.model.id == id).first()
        return self._execute_query(query)
    
    def get_multi(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get multiple records with pagination"""
        def query(db: Session):
            return db.query(self.model).offset(skip).limit(limit).all()
        return self._execute_query(query)
    
    def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record"""
        def query(db: Session):
            if isinstance(obj_in, dict):
                obj_data = obj_in
            else:
                obj_data = obj_in.model_dump() if hasattr(obj_in, 'model_dump') else obj_in.dict()
            db_obj = self.model(**obj_data)
            db.add(db_obj)
            db.flush()
            db.refresh(db_obj)
            return db_obj
        return self._execute_query(query)
    
    def update(self, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        """Update an existing record"""
        def query(db: Session):
            if isinstance(obj_in, dict):
                obj_data = obj_in
            elif hasattr(obj_in, 'model_dump'):
                obj_data = obj_in.model_dump(exclude_unset=True)
            else:
                obj_data = obj_in.dict(exclude_unset=True)
            
            # Re-attach object to session if needed
            merged_obj = db_obj
            if merged_obj not in db:
                merged_obj = db.merge(db_obj)
            
            for field, value in obj_data.items():
                setattr(merged_obj, field, value)
            
            db.flush()
            db.refresh(merged_obj)
            return merged_obj
        return self._execute_query(query)
    
    def delete(self, id: UUID) -> bool:
        """Delete a record by ID"""
        def query(db: Session):
            obj = db.query(self.model).filter(self.model.id == id).first()
            if obj:
                db.delete(obj)
                db.flush()
                return True
            return False
        return self._execute_query(query)