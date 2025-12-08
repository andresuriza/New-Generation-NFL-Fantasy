"""
Database error handling utilities and decorators
"""
import functools
from typing import Callable, Any
from sqlalchemy.exc import IntegrityError, DataError, DatabaseError
from services.constraint_error_service import constraint_error_service
from exceptions.business_exceptions import (
    ValidationError, 
    ConflictError, 
    NotFoundError, 
    ForeignKeyError, 
    ConstraintViolationError
)

def handle_db_errors(func: Callable) -> Callable:
    """
    Decorator to handle database errors consistently across all service methods
    Converts database errors to business exceptions
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IntegrityError as e:
            # Handle constraint violations - this will raise appropriate business exception
            constraint_error_service.handle_integrity_error(e)
        except DataError as e:
            # Handle data format errors - this will raise appropriate business exception
            constraint_error_service.handle_data_error(e)
        except DatabaseError as e:
            # Handle other database errors
            print(f"Database error in {func.__name__}: {e}")  # Log for debugging
            raise ValidationError("Error interno del servidor. Por favor, inténtelo más tarde.")
        except (ValidationError, ConflictError, NotFoundError, ForeignKeyError, ConstraintViolationError):
            # Re-raise business exceptions as-is
            raise
        except Exception as e:
            # Handle unexpected errors
            import traceback
            print(f"Unexpected error in {func.__name__}: {e}")  # Log for debugging
            print(f"Traceback: {traceback.format_exc()}")  # Log full traceback
            raise ValidationError("Error interno del servidor. Por favor, inténtelo más tarde.")
    
    return wrapper

def handle_db_errors_async(func: Callable) -> Callable:
    """
    Async version of the database error handling decorator
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except IntegrityError as e:
            # Handle constraint violations - this will raise appropriate business exception
            constraint_error_service.handle_integrity_error(e)
        except DataError as e:
            # Handle data format errors - this will raise appropriate business exception
            constraint_error_service.handle_data_error(e)
        except DatabaseError as e:
            # Handle other database errors
            print(f"Database error in {func.__name__}: {e}")  # Log for debugging
            raise ValidationError("Error interno del servidor. Por favor, inténtelo más tarde.")
        except (ValidationError, ConflictError, NotFoundError, ForeignKeyError, ConstraintViolationError):
            # Re-raise business exceptions as-is
            raise
        except Exception as e:
            # Handle unexpected errors
            print(f"Unexpected error in {func.__name__}: {e}")  # Log for debugging
            raise ValidationError("Error interno del servidor. Por favor, inténtelo más tarde.")
    
    return wrapper