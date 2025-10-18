# XNFL Fantasy API

FastAPI backend for New Generation NFL Fantasy. This API follows a thin-controller, service-layer architecture to keep endpoints simple and business logic centralized.

## Architecture

- `main.py`: FastAPI app creation and router wiring.
- `routers/`: HTTP endpoints (thin controllers) that:
  - Validate inputs via Pydantic schemas
  - Resolve dependencies (DB sessions, auth)
  - Delegate to services and return response models
- `services/`: Business logic and orchestration:
  - `auth_service.py`: Authentication, tokens, sessions
  - `email_service.py`: Azure Communication Services email send
  - `usuario_service.py`: Users: CRUD, profile updates, unlock flows, password policy
  - `equipo_service.py`: Teams: CRUD with domain constraints
  - `liga_service.py`: Leagues: list/get
  - `media_service.py`: In-memory media store (placeholder for CDN/DB)
   - `nfl_service.py`: Placeholder for external NFL API integration (schedule, teams, players, stats)
- `models/`: Pydantic request/response models and SQLAlchemy DB models
- `database.py`: DB session and Base

Key idea: Routers do not contain business rules. They call the appropriate service method, keeping responsibilities small and testable.

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

1. Define persistence model and Pydantic schemas:
   - `models/database_models.py`: add `StadiumDB` SQLAlchemy model
   - `models/stadium.py`: add `StadiumCreate`, `StadiumUpdate`, `StadiumResponse`

2. Create a service for business logic:
   - `services/stadium_service.py` with methods like `crear`, `listar`, `obtener`, `actualizar`, `eliminar`

3. Create a thin router:
   - `routers/stadiums.py` that injects `Session` with `Depends(get_db)` and delegates to `stadium_service`
   - Register in `main.py`: `app.include_router(stadiums.router, prefix="/api/stadiums", tags=["stadiums"])`

4. Test quickly:
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
