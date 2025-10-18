# XNFL Fantasy API - PowerShell Management Script
# Windows PowerShell equivalent of Makefile commands

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "XNFL Fantasy API Docker Commands (Windows)" -ForegroundColor Cyan
    Write-Host "=========================================="
    Write-Host ""
    Write-Host "Development Commands:" -ForegroundColor Yellow
    Write-Host "  up          - Start development environment"
    Write-Host "  up-d        - Start development environment in detached mode"
    Write-Host "  down        - Stop and remove containers"
    Write-Host "  build       - Build development containers"
    Write-Host "  restart     - Restart all services"
    Write-Host ""
    Write-Host "Production Commands:" -ForegroundColor Yellow
    Write-Host "  up-prod     - Start production environment"
    Write-Host "  down-prod   - Stop production environment"
    Write-Host "  build-prod  - Build production containers"
    Write-Host ""
    Write-Host "Utility Commands:" -ForegroundColor Yellow
    Write-Host "  logs        - Show API logs"
    Write-Host "  logs-db     - Show database logs"
    Write-Host "  shell       - Open shell in API container"
    Write-Host "  db-shell    - Open PostgreSQL shell"
    Write-Host ""
    Write-Host "Maintenance Commands:" -ForegroundColor Yellow
    Write-Host "  clean       - Clean up containers and volumes"
    Write-Host "  reset       - Reset everything (clean + rebuild)"
    Write-Host "  status      - Check container status"
    Write-Host "  health      - Check container health"
    Write-Host ""
    Write-Host "Database Commands:" -ForegroundColor Yellow
    Write-Host "  db-backup   - Backup database"
    Write-Host ""
    Write-Host "Usage: .\docker-manage.ps1 <command>"
    Write-Host "Example: .\docker-manage.ps1 up"
}

function Start-Development {
    Write-Host "Starting development environment..." -ForegroundColor Green
    docker-compose up --build
}

function Start-DevelopmentDetached {
    Write-Host "Starting development environment in detached mode..." -ForegroundColor Green
    docker-compose up --build -d
}

function Stop-Services {
    Write-Host "Stopping services..." -ForegroundColor Yellow
    docker-compose down
}

function Build-Development {
    Write-Host "Building development containers..." -ForegroundColor Green
    docker-compose build
}

function Restart-Services {
    Write-Host "Restarting services..." -ForegroundColor Yellow
    docker-compose restart
}

function Start-Production {
    Write-Host "Starting production environment..." -ForegroundColor Green
    docker-compose -f docker-compose.prod.yml up --build -d
}

function Stop-Production {
    Write-Host "Stopping production environment..." -ForegroundColor Yellow
    docker-compose -f docker-compose.prod.yml down
}

function Build-Production {
    Write-Host "Building production containers..." -ForegroundColor Green
    docker-compose -f docker-compose.prod.yml build
}

function Show-Logs {
    Write-Host "Showing API logs..." -ForegroundColor Cyan
    docker-compose logs -f api
}

function Show-DatabaseLogs {
    Write-Host "Showing database logs..." -ForegroundColor Cyan
    docker-compose logs -f postgres
}

function Open-Shell {
    Write-Host "Opening shell in API container..." -ForegroundColor Cyan
    docker-compose exec api bash
}

function Open-DatabaseShell {
    Write-Host "Opening PostgreSQL shell..." -ForegroundColor Cyan
    docker-compose exec postgres psql -U postgres -d XNFL-Fantasy
}

function Clean-Environment {
    Write-Host "Cleaning up containers and volumes..." -ForegroundColor Red
    docker-compose down -v
    docker system prune -f
}

function Reset-Environment {
    Write-Host "Resetting everything..." -ForegroundColor Red
    docker-compose down -v
    docker system prune -a -f
    docker-compose up --build
}

function Show-Status {
    Write-Host "Container Status:" -ForegroundColor Cyan
    docker-compose ps
}

function Show-Health {
    Write-Host "Container Health:" -ForegroundColor Cyan
    
    $apiHealth = docker inspect --format='{{.State.Health.Status}}' xnfl_api 2>$null
    if ($apiHealth) {
        Write-Host "API Health: $apiHealth" -ForegroundColor Green
    } else {
        Write-Host "API Health: Container not running" -ForegroundColor Red
    }
    
    $dbHealth = docker inspect --format='{{.State.Health.Status}}' xnfl_postgres 2>$null
    if ($dbHealth) {
        Write-Host "Database Health: $dbHealth" -ForegroundColor Green
    } else {
        Write-Host "Database Health: Container not running" -ForegroundColor Red
    }
}

function Backup-Database {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "backup_$timestamp.sql"
    Write-Host "Creating database backup: $backupFile" -ForegroundColor Green
    docker-compose exec postgres pg_dump -U postgres XNFL-Fantasy > $backupFile
    Write-Host "Backup completed: $backupFile" -ForegroundColor Green
}

# Command routing
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "up" { Start-Development }
    "up-d" { Start-DevelopmentDetached }
    "down" { Stop-Services }
    "build" { Build-Development }
    "restart" { Restart-Services }
    "up-prod" { Start-Production }
    "down-prod" { Stop-Production }
    "build-prod" { Build-Production }
    "logs" { Show-Logs }
    "logs-db" { Show-DatabaseLogs }
    "shell" { Open-Shell }
    "db-shell" { Open-DatabaseShell }
    "clean" { Clean-Environment }
    "reset" { Reset-Environment }
    "status" { Show-Status }
    "health" { Show-Health }
    "db-backup" { Backup-Database }
    default { 
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Run '.\docker-manage.ps1 help' for available commands"
    }
}