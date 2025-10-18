# 🪟 XNFL Fantasy API - Windows Setup Guide

## ✅ Windows Compatibility

**Good News!** The Docker setup works perfectly on Windows. Here's everything you need to know:

## 📋 Prerequisites for Windows

### 1. Install Docker Desktop
- Download from: https://www.docker.com/products/docker-desktop/
- Ensure **WSL 2** is enabled (recommended)
- Or use **Hyper-V** if WSL 2 isn't available

### 2. Install Git (if not already installed)
- Download from: https://git-scm.com/download/win

### 3. Choose Your Terminal
**Option A: PowerShell (Recommended)**
- Built into Windows
- Use the provided `docker-manage.ps1` script

**Option B: Command Prompt**
- Use the provided `docker-commands.bat` file

**Option C: Git Bash**
- Comes with Git installation
- Can use Linux commands and Makefile

## 🚀 Quick Start on Windows

### Method 1: PowerShell (Recommended)
```powershell
# Navigate to Backend directory
cd Backend

# Start development environment
.\docker-manage.ps1 up

# Or use individual Docker Compose commands
docker-compose up --build
```

### Method 2: Command Prompt
```cmd
cd Backend
docker-commands.bat up
```

### Method 3: Git Bash (Linux-like experience)
```bash
cd Backend
make up
# Or
docker-compose up --build
```

## 🛠 Windows-Specific Files Created

- **`docker-manage.ps1`** - PowerShell management script
- **`docker-commands.bat`** - Batch file for CMD
- **`start.bat`** - Windows startup script (used inside container)
- All original Linux files still work via Git Bash/WSL

## 💻 Common Windows Commands

### PowerShell Commands
```powershell
# Start services
.\docker-manage.ps1 up

# View logs
.\docker-manage.ps1 logs

# Access database
.\docker-manage.ps1 db-shell

# Stop services
.\docker-manage.ps1 down

# Get help
.\docker-manage.ps1 help
```

### Command Prompt Commands
```cmd
docker-commands.bat up
docker-commands.bat logs
docker-commands.bat down
docker-commands.bat help
```

### Docker Compose (Works in all terminals)
```cmd
docker-compose up --build
docker-compose logs api
docker-compose down
docker-compose ps
```

## 🔧 Windows-Specific Configuration

### File Paths
- Windows uses backslashes `\` but Docker handles this automatically
- Volume mounts work seamlessly
- All paths in Docker containers remain Linux-style

### Environment Variables
- The `.env` file works identically on Windows
- Use the same format as Linux/macOS

### Port Binding
- Same ports work on Windows: `localhost:8000` for API
- Database accessible at `localhost:5432`

## 🐛 Windows Troubleshooting

### Common Issues & Solutions

#### 1. **Docker Desktop not starting**
```powershell
# Ensure WSL 2 is installed
wsl --install
# Restart Docker Desktop
```

#### 2. **PowerShell execution policy**
```powershell
# Allow script execution (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 3. **Port conflicts**
```powershell
# Check what's using port 8000
netstat -ano | findstr :8000
# Kill process if needed
taskkill /PID <process_id> /F
```

#### 4. **Volume mount issues**
- Ensure Docker Desktop has access to your drive
- Go to Docker Desktop → Settings → Resources → File Sharing

#### 5. **Line ending issues**
```bash
# In Git Bash, fix line endings
git config core.autocrlf true
```

## 📁 Windows Directory Structure

Your Backend directory should look like:
```
Backend/
├── API/                     # Your FastAPI code
├── SQL_scripts/             # Database initialization
├── docker-compose.yml       # Development environment
├── docker-compose.prod.yml  # Production environment
├── Dockerfile               # Development image
├── Dockerfile.prod          # Production image
├── .env                     # Environment variables
├── .env.example            # Template
├── Makefile                # For Git Bash users
├── docker-manage.ps1       # PowerShell script
├── docker-commands.bat     # Command Prompt script
├── start.sh                # Linux startup script
├── start.bat               # Windows startup script
└── README.Docker.md        # Documentation
```

## 🎯 Development Workflow on Windows

1. **Open your terminal** (PowerShell, CMD, or Git Bash)
2. **Navigate to Backend directory**
   ```cmd
   cd path\to\New-Generation-NFL-Fantasy\Backend
   ```
3. **Start development environment**
   ```powershell
   .\docker-manage.ps1 up
   ```
4. **Open browser** → http://localhost:8000/docs
5. **Make code changes** → API auto-reloads
6. **View logs when needed**
   ```powershell
   .\docker-manage.ps1 logs
   ```

## 🔒 Windows Security Notes

- Docker containers run in isolated environment
- Windows Defender may scan container files (normal)
- Firewall rules are automatically handled by Docker Desktop

## 🎉 Windows Benefits

✅ **Native Windows integration**
✅ **Same performance as Linux/macOS**
✅ **Full Docker feature support**
✅ **Multiple terminal options**
✅ **Visual Studio Code integration**
✅ **Windows-native scripts provided**

## 📞 Windows Support

If you encounter Windows-specific issues:

1. **Check Docker Desktop logs**
2. **Verify WSL 2 installation**
3. **Ensure proper file permissions**
4. **Try different terminal (PowerShell vs CMD vs Git Bash)**

The Docker setup is fully cross-platform and provides the same functionality on Windows, macOS, and Linux! 🎉