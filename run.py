#!/usr/bin/env python3
"""
GLASS Data Standardizer v2.0.0 - Streamlit Launcher
Simple launcher for the Streamlit application.
"""

import sys
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
        sys.exit(1)
    
    # Check if app.py exists
    if not Path("app.py").exists():
        print("❌ Error: app.py not found")
        print("Please ensure you're running this from the project root directory")
        sys.exit(1)
    
    print("🚀 Launching GLASS Data Standardizer...")
    print("🔗 URL: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the application")
    print("-" * 50)
    
    # Launch Streamlit
    try:
        import subprocess
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port=8501",
            "--server.address=localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()




