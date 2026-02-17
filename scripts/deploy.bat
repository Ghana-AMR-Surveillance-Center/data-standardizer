@echo off
REM AMR Data Harmonizer - Production Deployment Script (Windows)

echo 🚀 AMR Data Harmonizer - Production Deployment
echo ==================================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    exit /b 1
)

echo ✓ Python found

REM Check if virtual environment exists
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo 📥 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Check environment variables
echo 🔍 Checking environment configuration...
if "%ENVIRONMENT%"=="" (
    echo ⚠️  ENVIRONMENT not set, defaulting to production
    set ENVIRONMENT=production
)

if "%SECRET_KEY%"=="" (
    echo ⚠️  SECRET_KEY not set, generating one...
    for /f "delims=" %%i in ('python -c "import secrets; print(secrets.token_urlsafe(32))"') do set SECRET_KEY=%%i
    echo ⚠️  Please set SECRET_KEY in your environment for production!
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist "logs" mkdir logs
if not exist "data" mkdir data

REM Run pre-deployment checks
echo ✅ Running pre-deployment checks...
python -c "import sys; from config.production import production_config; production_config.validate_config()"

REM Start application
echo 🚀 Starting application...
echo ==================================================
python run_production.py
