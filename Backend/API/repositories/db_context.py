"""
Database session context manager for repositories
This ensures only repositories have access to database sessions
"""
from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session
from database import SessionLocal


class DatabaseContext:
    """Context manager for database sessions"""
    
    @staticmethod
    @contextmanager
    def get_session() -> Generator[Session, None, None]:
        """
        Context manager that provides a database session.
        Automatically handles commit/rollback and cleanup.
        """
        db = SessionLocal()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    
    @staticmethod
    def execute_in_transaction(func, *args, **kwargs):
        """
        Execute a function within a database transaction.
        Handles session lifecycle automatically.
        """
        with DatabaseContext.get_session() as db:
            return func(db, *args, **kwargs)


# Singleton instance
db_context = DatabaseContext()
