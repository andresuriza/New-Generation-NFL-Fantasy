"""
Router exception handlers to convert business exceptions to HTTP responses
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from exceptions.business_exceptions import (
    ValidationError, 
    ConflictError, 
    NotFoundError, 
    ForeignKeyError, 
    ConstraintViolationError,
    BusinessLogicError
)

def create_business_exception_handlers(app):
    """Add business exception handlers to FastAPI app"""
    
    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=400,
            content={"detail": exc.message, "error_code": exc.error_code}
        )
    
    @app.exception_handler(ConflictError)
    async def conflict_error_handler(request: Request, exc: ConflictError):
        return JSONResponse(
            status_code=409,
            content={"detail": exc.message, "error_code": exc.error_code}
        )
    
    @app.exception_handler(NotFoundError)
    async def not_found_error_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=404,
            content={"detail": exc.message, "error_code": exc.error_code}
        )
    
    @app.exception_handler(ForeignKeyError)
    async def foreign_key_error_handler(request: Request, exc: ForeignKeyError):
        return JSONResponse(
            status_code=400,
            content={"detail": exc.message, "error_code": exc.error_code}
        )
    
    @app.exception_handler(ConstraintViolationError)
    async def constraint_violation_error_handler(request: Request, exc: ConstraintViolationError):
        return JSONResponse(
            status_code=400,
            content={
                "detail": exc.message, 
                "error_code": exc.error_code,
                "constraint_type": exc.constraint_type,
                "constraint_name": exc.constraint_name
            }
        )
    
    @app.exception_handler(BusinessLogicError)
    async def business_logic_error_handler(request: Request, exc: BusinessLogicError):
        return JSONResponse(
            status_code=400,
            content={"detail": exc.message, "error_code": exc.error_code}
        )