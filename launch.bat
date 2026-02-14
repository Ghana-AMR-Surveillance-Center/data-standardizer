@echo off
REM AMR Data Harmonizer - Docker Launcher
echo ============================================================
echo 🏥 AMR Data Harmonizer v2.0.0
echo ============================================================
echo Production Ready - Data Processing ^& Standardization Platform
echo ============================================================

REM Check if Docker is installed and running
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed or not in PATH
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker daemon is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

echo ✅ Docker is installed and running

REM Check if Docker image exists, build if it doesn't
docker images amr-data-harmonizer:latest --format "{{.Repository}}:{{.Tag}}" | findstr /C:"amr-data-harmonizer:latest" >nul
if errorlevel 1 (
    echo 📦 Building Docker image...
    docker build -t amr-data-harmonizer:latest .
    if errorlevel 1 (
        echo ❌ Failed to build Docker image
        pause
        exit /b 1
    )
    echo ✅ Docker image built successfully
) else (
    echo ✅ Docker image found
)

REM Stop and remove existing container if it exists
docker ps -a --filter "name=amr-data-harmonizer" --format "{{.Names}}" | findstr /C:"amr-data-harmonizer" >nul
if not errorlevel 1 (
    echo 🛑 Stopping existing container...
    docker stop amr-data-harmonizer >nul 2>&1
    docker rm amr-data-harmonizer >nul 2>&1
)

REM Create necessary directories if they don't exist
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "config" mkdir config

echo.
echo 🚀 Launching AMR Data Harmonizer in Docker...
echo 📱 The application will open in your default web browser
echo 🔗 URL: http://localhost:8501
echo ⏹️  Press Ctrl+C to stop the application
echo --------------------------------------------------

REM Run Docker container
docker run --rm -it ^
    --name amr-data-harmonizer ^
    -p 8501:8501 ^
    -v "%CD%\data:/app/data" ^
    -v "%CD%\logs:/app/logs" ^
    -v "%CD%\config:/app/config" ^
    -e ENVIRONMENT=development ^
    -e DEBUG=true ^
    -e LOG_LEVEL=INFO ^
    amr-data-harmonizer:latest

pause
