#!/usr/bin/env python3
"""
GLASS Data Standardizer - Main Production Launcher
Clean, production-ready launcher for deployment
"""

import sys
import subprocess
import os
from pathlib import Path

def main():
    """Main launcher function."""
    print("🏥 GLASS Data Standardizer v2.0.0 - Production Ready")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Check if virtual environment exists
    venv_path = Path(".venv")
    if not venv_path.exists():
        print("❌ Virtual environment not found")
        print("Please run setup.py first to create the environment")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Get the correct Python executable
    if os.name == 'nt':  # Windows
        python_exe = venv_path / "Scripts" / "python.exe"
    else:  # Unix/Linux/macOS
        python_exe = venv_path / "bin" / "python"
    
    if not python_exe.exists():
        print("❌ Python executable not found in virtual environment")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Check if app.py exists
    app_path = Path("app.py")
    if not app_path.exists():
        print("❌ app.py not found")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print("🚀 Launching GLASS Data Standardizer...")
    print("📱 The application will open in your default web browser")
    print("🔗 URL: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        # Launch Streamlit
        subprocess.run([
            str(python_exe), "-m", "streamlit", "run", 
            str(app_path),
            "--server.port", "8501",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
