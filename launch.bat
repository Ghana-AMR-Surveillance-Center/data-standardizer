@echo off
REM GLASS Data Standardizer - Easy Launcher
echo ============================================================
echo 🏥 GLASS Data Standardizer v2.0.0
echo ============================================================
echo Production Ready - Data Processing & Standardization Platform
echo ============================================================

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Set development environment variables
set ENVIRONMENT=development
set SECRET_KEY=dev-secret-key-12345
set HOST=0.0.0.0
set PORT=8501

echo ✅ Virtual environment activated
echo ✅ Environment variables set for development
echo.
echo 🚀 Launching GLASS Data Standardizer...
echo 📱 The application will open in your default web browser
echo 🔗 URL: http://localhost:8501
echo ⏹️  Press Ctrl+C to stop the application
echo --------------------------------------------------

REM Launch the application
python run.py

pause
