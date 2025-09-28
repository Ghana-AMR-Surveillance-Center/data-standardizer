@echo off
REM GLASS Data Standardizer - Windows Launcher
REM Clean production launcher

echo ============================================================
echo  GLASS Data Standardizer v2.0.0
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

echo Python found. Checking version...
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"
if errorlevel 1 (
    echo ERROR: Python 3.8 or higher is required
    echo Current version:
    python --version
    pause
    exit /b 1
)

echo Python version OK.

REM Check if virtual environment exists
if not exist ".venv" (
    echo Virtual environment not found. Running setup...
    python setup.py
    if errorlevel 1 (
        echo Setup failed. Please check the error messages above.
        pause
        exit /b 1
    )
)

REM Launch the application
echo Launching GLASS Data Standardizer...
python run.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Application exited with an error
    pause
)
