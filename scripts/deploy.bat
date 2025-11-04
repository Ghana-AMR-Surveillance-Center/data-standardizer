@echo off
REM GLASS Data Standardizer - Production Deployment Script for Windows

setlocal enabledelayedexpansion

REM Configuration
set APP_NAME=glass-data-standardizer
set VERSION=2.0.0
set DOCKER_IMAGE=glass-data-standardizer:latest
set CONTAINER_NAME=glass-data-standardizer-prod
set PORT=8501

echo [INFO] Starting deployment of %APP_NAME% v%VERSION%
echo ==============================================

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Check if required directories exist
echo [INFO] Checking required directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "config" mkdir config
if not exist "ssl" mkdir ssl

REM Build Docker image
echo [INFO] Building Docker image...
docker build -t %DOCKER_IMAGE% .
if errorlevel 1 (
    echo [ERROR] Failed to build Docker image
    exit /b 1
)
echo [INFO] Docker image built successfully

REM Stop existing container
echo [INFO] Stopping existing container...
docker ps -q -f name=%CONTAINER_NAME% | findstr . >nul
if not errorlevel 1 (
    docker stop %CONTAINER_NAME%
    echo [INFO] Container stopped
) else (
    echo [INFO] No running container found
)

docker ps -aq -f name=%CONTAINER_NAME% | findstr . >nul
if not errorlevel 1 (
    docker rm %CONTAINER_NAME%
    echo [INFO] Container removed
)

REM Start new container
echo [INFO] Starting new container...
docker run -d ^
    --name %CONTAINER_NAME% ^
    --restart unless-stopped ^
    -p %PORT%:8501 ^
    -v "%CD%\data:/app/data" ^
    -v "%CD%\logs:/app/logs" ^
    -v "%CD%\config:/app/config" ^
    -e ENVIRONMENT=production ^
    -e DEBUG=false ^
    -e LOG_LEVEL=INFO ^
    -e HOST=0.0.0.0 ^
    -e PORT=8501 ^
    -e MAX_FILE_SIZE_MB=100 ^
    -e ENABLE_MONITORING=true ^
    %DOCKER_IMAGE%

if errorlevel 1 (
    echo [ERROR] Failed to start container
    exit /b 1
)
echo [INFO] Container started successfully

REM Check container health
echo [INFO] Checking container health...
timeout /t 10 /nobreak >nul

REM Check if container is running
docker ps -q -f name=%CONTAINER_NAME% | findstr . >nul
if errorlevel 1 (
    echo [ERROR] Container is not running
    docker logs %CONTAINER_NAME%
    exit /b 1
)

REM Check if application is responding
for /L %%i in (1,1,30) do (
    curl -f http://localhost:%PORT%/_stcore/health >nul 2>&1
    if not errorlevel 1 (
        echo [INFO] Application is healthy and responding
        goto :health_ok
    )
    echo [INFO] Waiting for application to start... (%%i/30)
    timeout /t 2 /nobreak >nul
)

echo [ERROR] Application failed to start or is not responding
docker logs %CONTAINER_NAME%
exit /b 1

:health_ok
REM Show deployment status
echo.
echo [INFO] Deployment Status:
echo ==================
echo Application: %APP_NAME% v%VERSION%
echo Container: %CONTAINER_NAME%
echo Port: %PORT%
echo URL: http://localhost:%PORT%
echo.

REM Show container status
docker ps -f name=%CONTAINER_NAME% --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.

REM Show recent logs
echo [INFO] Recent logs:
docker logs --tail 10 %CONTAINER_NAME%

REM Cleanup old images
echo [INFO] Cleaning up old images...
docker image prune -f

echo.
echo [INFO] Deployment completed successfully!
echo [INFO] Application is available at: http://localhost:%PORT%
echo.
echo To view logs: docker logs -f %CONTAINER_NAME%
echo To stop: docker stop %CONTAINER_NAME%
echo To restart: docker restart %CONTAINER_NAME%
