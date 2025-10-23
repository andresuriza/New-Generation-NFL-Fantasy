# XNFL Fantasy API

FastAPI backend for New Generation NFL Fantasy. This API follows a layered architecture with separation of concerns using the repository pattern to maintain clean, testable, and maintainable code.

## Architecture

The application is structured in three main layers:

- `main.py`: FastAPI app creation and router wiring.
- `routers/`: HTTP endpoints (presentation layer) that:
  - Validate inputs via Pydantic schemas
  - Resolve dependencies (DB sessions, auth)
  - Delegate to services and return response models
- `services/`: Business logic layer:
  - `auth_service.py`: Authentication, tokens, sessions
  - `email_service.py`: Azure Communication Services email send
  - `usuario_service.py`: Users: CRUD, profile updates, unlock flows, password policy
  - `equipo_service.py`: Teams: CRUD with domain constraints
  - `liga_service.py`: Leagues: management and operations
  - `temporada_service.py`: Season management and business rules
  - `media_service.py`: Media handling and storage operations
  - `nfl_service.py`: External NFL API integration (schedule, teams, players, stats)
- `repositories/`: Data access layer implementing repository pattern:
  - `base.py`: Generic repository base class with common CRUD operations
  - `liga_repository.py`: League-specific database operations
  - `equipo_repository.py`: Team-specific database operations
  - `temporada_repository.py`: Season-specific database operations
  - `usuario_repository.py`: User-specific database operations
  - `media_repository.py`: Media-specific database operations
- `models/`: Data models:
  - `database_models.py`: SQLAlchemy ORM models
  - Individual model files: Pydantic request/response schemas
- `database.py`: Database session management and configuration

Key principles: Clean separation of concerns with routers handling HTTP, services containing business logic, and repositories managing data access. Each layer has a single responsibility and dependencies flow inward.

## Local development

This project assumes a Python virtual environment at `Backend/venv`.

1. Activate the virtual env and run the API:

```bash
cd Backend/API
source ../venv/bin/activate
python run_server.py
```

2. Open the docs at:
```
http://localhost:8000/docs
```

If you need to install dependencies into your venv, use `Backend/requirements.txt` from the repo root:

```bash
cd Backend
source venv/bin/activate
pip install -r requirements.txt
```

## Adding a new module (resource)

Example: Add a new resource `stadiums`.

1. Define data models:
   - `models/database_models.py`: add `StadiumDB` SQLAlchemy model
   - `models/stadium.py`: add `StadiumCreate`, `StadiumUpdate`, `StadiumResponse` Pydantic schemas

2. Create repository for data access:
   - `repositories/stadium_repository.py`: extend `BaseRepository` with stadium-specific queries
   - Add to `repositories/__init__.py` for proper module imports

3. Create service for business logic:
   - `services/stadium_service.py` with methods like `crear`, `listar`, `obtener`, `actualizar`, `eliminar`
   - Inject and use `stadium_repository` for all database operations

4. Create router for HTTP endpoints:
   - `routers/stadiums.py` that injects `Session` with `Depends(get_db)` and delegates to `stadium_service`
   - Register in `main.py`: `app.include_router(stadiums.router, prefix="/api/stadiums", tags=["stadiums"])`

5. Test integration:
   - Import check in venv:
     ```bash
     cd Backend/API && source ../venv/bin/activate
     python -c "import routers.stadiums; print('OK')"
     ```
   - Hit endpoints via Swagger UI or HTTP client


## Environment variables

- `SECRET_KEY`, `ALGORITHM`: JWT config (see `auth_service.py`)
- `UNLOCK_TOKEN_EXPIRE_MINUTES` (default: `60`)
- `FRONTEND_PUBLIC_URL` (default: `http://localhost:3000`)
- `AZURE_COMMUNICATION_EMAIL_CONNECTION_STRING`, `AZURE_EMAIL_SENDER` (optional; unlock emails)
- `NFL_API_BASE_URL`, `NFL_API_KEY` (optional; configure when implementing `nfl_service`)
