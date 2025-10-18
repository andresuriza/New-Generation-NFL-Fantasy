@echo off
REM Windows batch script to start XNFL Fantasy API

echo [INFO] Starting XNFL Fantasy API...

REM Colors aren't easily available in batch, so using plain text
echo [INFO] Waiting for PostgreSQL to be ready...

REM Wait for database using Docker
:wait_for_db
docker-compose exec postgres pg_isready -h postgres -p 5432 -U postgres >nul 2>&1
if errorlevel 1 (
    timeout /t 2 >nul
    goto wait_for_db
)

echo [SUCCESS] PostgreSQL is ready!

REM Start the FastAPI application
echo [INFO] Starting FastAPI application...
uvicorn main:app --host 0.0.0.0 --port 8000 --reload