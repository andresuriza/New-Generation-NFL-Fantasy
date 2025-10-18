@echo off
REM Windows batch file for Docker operations
REM Alternative to Makefile for Windows users

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="up" goto up
if "%1"=="down" goto down
if "%1"=="build" goto build
if "%1"=="logs" goto logs
if "%1"=="shell" goto shell
if "%1"=="db-shell" goto db-shell
if "%1"=="clean" goto clean
if "%1"=="status" goto status
goto unknown

:help
echo XNFL Fantasy API Docker Commands (Windows)
echo ==========================================
echo.
echo Available commands:
echo   up       - Start development environment
echo   down     - Stop services
echo   build    - Build containers
echo   logs     - Show API logs
echo   shell    - Open shell in API container
echo   db-shell - Open database shell
echo   clean    - Clean up containers
echo   status   - Show container status
echo.
echo Usage: docker-commands.bat ^<command^>
echo Example: docker-commands.bat up
goto end

:up
echo Starting development environment...
docker-compose up --build
goto end

:down
echo Stopping services...
docker-compose down
goto end

:build
echo Building containers...
docker-compose build
goto end

:logs
echo Showing API logs...
docker-compose logs -f api
goto end

:shell
echo Opening shell in API container...
docker-compose exec api bash
goto end

:db-shell
echo Opening PostgreSQL shell...
docker-compose exec postgres psql -U postgres -d XNFL-Fantasy
goto end

:clean
echo Cleaning up containers and volumes...
docker-compose down -v
docker system prune -f
goto end

:status
echo Container status:
docker-compose ps
goto end

:unknown
echo Unknown command: %1
echo Run "docker-commands.bat help" for available commands
goto end

:end