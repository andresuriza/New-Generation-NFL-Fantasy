# XNFL Fantasy API - Docker Setup

This directory contains the Docker configuration for the XNFL Fantasy API backend.

## 🌍 Cross-Platform Support

✅ **Linux** - Full support with Makefile and bash scripts  
✅ **macOS** - Full support with Makefile and bash scripts  
✅ **Windows** - Full support with PowerShell (.ps1) and batch (.bat) scripts

> **Windows Users:** See `README.Windows.md` for Windows-specific setup instructions.

## 📁 Docker Files

- `Dockerfile` - Development Docker image
- `Dockerfile.prod` - Production-optimized Docker image  
- `docker-compose.yml` - Development environment with database
- `docker-compose.prod.yml` - Production environment
- `start.sh` - Startup script with database wait logic
- `.dockerignore` - Files to exclude from Docker build
- `.env.example` - Example environment variables

## 🚀 Quick Start

### Development Environment

1. **Copy environment variables:**
   ```bash
   cp .env.example .env
   ```

2. **Start the development environment:**
   ```bash
   docker-compose up --build
   ```

3. **Access the API:**
   - API Documentation: http://localhost:8000/docs
   - API Redoc: http://localhost:8000/redoc
   - Database: localhost:5432

### Production Environment

1. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your production values
   ```

2. **Start production environment:**
   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

## 🛠 Available Commands

### Development Commands

**Linux/macOS:**
```bash
# Using Makefile shortcuts
make up          # Start development environment
make logs        # View API logs
make shell       # Access API container
make db-shell    # Access database
make down        # Stop services

# Or using Docker Compose directly
docker-compose up --build
docker-compose logs api
docker-compose down
```

**Windows PowerShell:**
```powershell
# Using PowerShell script
.\docker-manage.ps1 up      # Start development environment
.\docker-manage.ps1 logs    # View API logs
.\docker-manage.ps1 shell   # Access API container
.\docker-manage.ps1 down    # Stop services
```

**Windows Command Prompt:**
```cmd
# Using batch file
docker-commands.bat up      # Start development environment
docker-commands.bat logs    # View API logs
docker-commands.bat down    # Stop services
```

### Production Commands

```bash
# Start production services
docker-compose -f docker-compose.prod.yml up -d

# View production logs
docker-compose -f docker-compose.prod.yml logs

# Scale API instances (production)
docker-compose -f docker-compose.prod.yml up --scale api=3 -d
```

## 🗄 Database Management

### Initial Setup

The PostgreSQL database is automatically initialized with SQL scripts from the `SQL_scripts/` directory when the container starts for the first time.

### Database Access

```bash
# Connect to database via Docker
docker-compose exec postgres psql -U postgres -d XNFL-Fantasy

# Or using local psql client
psql -h localhost -p 5432 -U postgres -d XNFL-Fantasy
```

### Backup and Restore

```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres XNFL-Fantasy > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres XNFL-Fantasy < backup.sql
```

## 🔧 Configuration

### Environment Variables

Key environment variables (set in `.env` file):

- `POSTGRES_DB` - Database name (default: XNFL-Fantasy)
- `POSTGRES_USER` - Database user (default: postgres)  
- `POSTGRES_PASSWORD` - Database password
- `DATABASE_URL` - Full database connection string
- `API_PORT` - API port (default: 8000)
- `POSTGRES_PORT` - Database port (default: 5432)

### Custom Configuration

To modify the API configuration:

1. Edit the environment variables in `.env`
2. Restart the containers: `docker-compose restart`

## 🏥 Health Checks

Both the API and database containers include health checks:

- **API Health Check:** GET `/docs` endpoint
- **Database Health Check:** `pg_isready` command

Check service health:
```bash
docker-compose ps
```

## 📊 Monitoring

### View Container Status
```bash
# Check running containers
docker-compose ps

# View resource usage
docker stats

# Check container health
docker inspect --format='{{.State.Health.Status}}' xnfl_api
```

### Application Logs
```bash
# Follow API logs
docker-compose logs -f api

# View last 100 lines
docker-compose logs --tail=100 api

# View logs with timestamps
docker-compose logs -t api
```

## 🔄 Development Workflow

1. **Make code changes** - Files are mounted as volumes in development mode
2. **API auto-reloads** - Changes are automatically detected
3. **Test changes** - Visit http://localhost:8000/docs
4. **Check logs** - `docker-compose logs api`

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Change ports in docker-compose.yml or .env file
   API_PORT=8001
   POSTGRES_PORT=5433
   ```

2. **Database connection issues:**
   ```bash
   # Check database is ready
   docker-compose exec postgres pg_isready -U postgres
   
   # View database logs
   docker-compose logs postgres
   ```

3. **Permission issues:**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

4. **Clean rebuild:**
   ```bash
   # Remove containers and rebuild
   docker-compose down -v
   docker-compose build --no-cache
   docker-compose up
   ```

### Reset Everything

```bash
# Stop and remove containers, networks, and volumes
docker-compose down -v

# Remove unused Docker resources
docker system prune -a

# Rebuild from scratch
docker-compose up --build
```

## 📋 Production Deployment

For production deployment:

1. Use `docker-compose.prod.yml`
2. Set strong passwords in `.env`
3. Configure proper networking/firewall rules
4. Set up log aggregation
5. Configure backup strategies
6. Enable SSL/TLS termination (nginx/traefik)

Example production startup:
```bash
# Production deployment
export POSTGRES_PASSWORD=your_secure_password
docker-compose -f docker-compose.prod.yml up -d
```

## 🎯 API Endpoints

Once running, the API provides:

- **OpenAPI Documentation:** http://localhost:8000/docs
- **Alternative Documentation:** http://localhost:8000/redoc
- **API Base URL:** http://localhost:8000/api

### Main Endpoints:
- `/api/usuarios` - User management
- `/api/equipos` - Team management  
- `/api/ligas` - League management
- `/api/media` - Media handling
- `/api/chatgpt` - AI integration
- `/api/analytics` - Analytics endpoints