#!/usr/bin/env python3
"""
GLASS Data Standardizer - Setup Script
Creates virtual environment and installs dependencies
"""

import sys
import subprocess
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function."""
    print("=" * 60)
    print("🏥 GLASS Data Standardizer - Setup")
    print("=" * 60)
    print("Setting up production environment...")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Create virtual environment
    venv_path = Path(".venv")
    if venv_path.exists():
        print("⚠️  Virtual environment already exists")
        response = input("Do you want to recreate it? (y/N): ").lower()
        if response == 'y':
            print("🗑️  Removing existing virtual environment...")
            if os.name == 'nt':  # Windows
                os.system("rmdir /s /q .venv")
            else:  # Unix/Linux/macOS
                os.system("rm -rf .venv")
        else:
            print("✅ Using existing virtual environment")
    
    if not venv_path.exists():
        if not run_command(f"{sys.executable} -m venv .venv", "Creating virtual environment"):
            input("Press Enter to exit...")
            sys.exit(1)
    
    # Determine Python executable path
    if os.name == 'nt':  # Windows
        python_exe = venv_path / "Scripts" / "python.exe"
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:  # Unix/Linux/macOS
        python_exe = venv_path / "bin" / "python"
        pip_exe = venv_path / "bin" / "pip"
    
    # Upgrade pip
    if not run_command(f'"{pip_exe}" install --upgrade pip', "Upgrading pip"):
        print("⚠️  Warning: Could not upgrade pip, continuing...")
    
    # Install dependencies
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        if not run_command(f'"{pip_exe}" install -r requirements.txt', "Installing dependencies"):
            print("⚠️  Warning: Some dependencies may not have installed correctly")
    else:
        print("❌ requirements.txt not found")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Test installation
    print("🧪 Testing installation...")
    try:
        result = subprocess.run([
            str(python_exe), "-c", 
            "import streamlit, pandas, numpy, openpyxl; print('All dependencies imported successfully')"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Installation test passed")
        else:
            print("❌ Installation test failed")
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Setup completed!")
    print("=" * 60)
    print("To run the application:")
    print("  python run.py")
    print("  or")
    print("  .venv\\Scripts\\python.exe -m streamlit run app.py")
    print("=" * 60)
    
    input("Press Enter to continue...")

if __name__ == "__main__":
    main()
