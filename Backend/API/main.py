from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, DataError, DatabaseError
import traceback

from routers import usuarios, equipos, media, ligas, temporadas, chatgpt, analytics, jugadores, equipos_fantasy
from routers.exception_handlers import create_business_exception_handlers
from services.constraint_error_service import constraint_error_service

app = FastAPI(
    title="XNFL Fantasy API",
    description="API para la aplicación de Fantasy Football NFL",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    # Permitir orígenes locales comunes (incluye Swagger en 8000)
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add business exception handlers
create_business_exception_handlers(app)

# Global exception handlers for unhandled database errors
@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle unhandled database integrity errors globally"""
    try:
        constraint_error_service.handle_integrity_error(exc)
    except Exception as business_exc:
        # This should be handled by business exception handlers, but just in case
        return JSONResponse(
            status_code=400,
            content={"detail": str(business_exc)}
        )

@app.exception_handler(DataError)
async def data_error_handler(request: Request, exc: DataError):
    """Handle unhandled database data errors globally"""
    try:
        constraint_error_service.handle_data_error(exc)
    except Exception as business_exc:
        # This should be handled by business exception handlers, but just in case
        return JSONResponse(
            status_code=400,
            content={"detail": str(business_exc)}
        )

@app.exception_handler(DatabaseError)
async def database_error_handler(request: Request, exc: DatabaseError):
    """Handle general database errors"""
    # Log the full error for debugging
    print(f"Database error: {exc}")
    print(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor. Por favor, inténtelo más tarde."}
    )

# Incluir los routers
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["usuarios"])
app.include_router(equipos.router, prefix="/api/equipos", tags=["equipos"])
app.include_router(equipos_fantasy.router, prefix="/api", tags=["equipos-fantasy"])
app.include_router(media.router, prefix="/api/media", tags=["media"])
app.include_router(ligas.router, prefix="/api/ligas", tags=["ligas"])
app.include_router(temporadas.router, prefix="/api/temporadas", tags=["temporadas"])
app.include_router(chatgpt.router, prefix="/api/chatgpt", tags=["chatgpt"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(jugadores.router, prefix="/api/jugadores", tags=["jugadores"])

@app.get("/")
def read_root():
    return {"message": "¡Bienvenido a XNFL Fantasy API!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}