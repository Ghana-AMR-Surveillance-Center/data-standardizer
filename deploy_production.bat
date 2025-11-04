@echo off
REM GLASS Data Standardizer v2.0.0 - Production Deployment Script
REM This script deploys the application in production mode

echo ============================================================
echo 🏥 GLASS Data Standardizer v2.0.0 - Production Deployment
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo ✅ Python detected

REM Check if virtual environment exists
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install/upgrade dependencies
echo 📚 Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "config" mkdir config

REM Set production environment variables
echo ⚙️ Setting production environment variables...
set "ENVIRONMENT=production"
if "%SECRET_KEY%"=="" (
    echo ❌ ERROR: SECRET_KEY environment variable is not set!
    echo    Please set SECRET_KEY before running this script:
    echo    set "SECRET_KEY=your-secure-secret-key-here"
    echo    Or use a .env file or secret management service.
    pause
    exit /b 1
)
set "HOST=0.0.0.0"
set "PORT=8501"
set "LOG_LEVEL=INFO"

REM Validate configuration
echo 🔍 Validating configuration...
python -c "from config.production import production_config; print('✅ Configuration valid' if production_config.validate_config() else '❌ Configuration invalid')"
if %errorlevel% neq 0 (
    echo ❌ Configuration validation failed
    pause
    exit /b 1
)

REM Start the application
echo.
echo 🚀 Starting GLASS Data Standardizer in production mode...
echo 📱 The application will be available at: http://localhost:8501
echo ⏹️  Press Ctrl+C to stop the application
echo.

python run_production.py

echo.
echo 👋 Application stopped
pause
