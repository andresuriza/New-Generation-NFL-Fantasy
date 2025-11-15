"""
Custom business logic exceptions for the NFL Fantasy API
These exceptions are thrown by services and handled by routers
"""

class BusinessLogicError(Exception):
    """Base class for business logic errors"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ValidationError(BusinessLogicError):
    """Raised when data validation fails"""
    pass

class ConflictError(BusinessLogicError):
    """Raised when there's a conflict (e.g., duplicate data)"""
    pass

class NotFoundError(BusinessLogicError):
    """Raised when a requested resource is not found"""
    pass

class ForeignKeyError(BusinessLogicError):
    """Raised when a foreign key reference is invalid"""
    pass

class ConstraintViolationError(BusinessLogicError):
    """Raised when a database constraint is violated"""
    def __init__(self, message: str, constraint_type: str = None, constraint_name: str = None):
        self.constraint_type = constraint_type
        self.constraint_name = constraint_name
        super().__init__(message)