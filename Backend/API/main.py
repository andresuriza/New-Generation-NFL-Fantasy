from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import usuarios, equipos, media, ligas

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

# Incluir los routers
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["usuarios"])
app.include_router(equipos.router, prefix="/api/equipos", tags=["equipos"])
app.include_router(media.router, prefix="/api/media", tags=["media"])
app.include_router(ligas.router, prefix="/api/ligas", tags=["ligas"])

@app.get("/")
async def root():
    return {"message": "XNFL Fantasy API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}