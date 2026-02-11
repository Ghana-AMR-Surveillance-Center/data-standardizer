#!/usr/bin/env python3
"""
GLASS Data Standardizer - Production Launcher
Enhanced with production features and monitoring
"""

import sys
import os
import subprocess
import time
import signal
import atexit
from pathlib import Path
from typing import Optional

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'streamlit', 'pandas', 'plotly', 'numpy', 
        'openpyxl', 'xlsxwriter', 'psutil'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing dependencies: {', '.join(missing_packages)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    return True

def check_environment():
    """Check production environment configuration"""
    try:
        from config.production import production_config
        
        if not production_config.validate_config():
            print("⚠️  Production configuration validation failed - using defaults")
            return False
        
        return True
    except ImportError:
        print("⚠️  Production configuration not found - using defaults")
        return False

def setup_logging():
    """Setup production logging"""
    try:
        from utils.production_logger import initialize_production_logger
        from config.production import production_config
        
        logger = initialize_production_logger(production_config.get_logging_config())
        logger.log_application_start(production_config.version, production_config.environment)
        return logger
    except Exception as e:
        print(f"⚠️  Could not setup production logging: {e}")
        return None

def setup_health_monitoring():
    """Setup health monitoring"""
    try:
        from utils.health_monitor import health_monitor
        return health_monitor
    except Exception as e:
        print(f"⚠️  Could not setup health monitoring: {e}")
        return None

def setup_security():
    """Setup security features"""
    try:
        from utils.security import security_manager
        return security_manager
    except Exception as e:
        print(f"⚠️  Could not setup security features: {e}")
        return None

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\n🛑 Shutdown signal received...")
    
    try:
        from utils.production_logger import get_production_logger
        logger = get_production_logger()
        if logger:
            logger.log_application_stop("signal")
    except Exception:
        pass
    
    print("👋 Application stopped")
    sys.exit(0)

def launch_application():
    """Launch the Streamlit application with production settings"""
    print("🚀 Launching GLASS Data Standardizer...")
    print("🔗 URL: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the application")
    print("--------------------------------------------------")
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Register cleanup function
    atexit.register(lambda: print("👋 Application stopped"))
    
    try:
        # Get production configuration
        try:
            from config.production import production_config
            port = production_config.port
            host = production_config.host
        except ImportError:
            port = 8501
            host = "0.0.0.0"
        
        # Launch Streamlit with production settings
        cmd = [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", str(port),
            "--server.address", host,
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "true"
        ]
        
        # Add additional production settings
        if os.getenv('ENVIRONMENT') == 'production':
            cmd.extend([
                "--server.maxUploadSize", "100",
                "--server.maxMessageSize", "100"
            ])
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        sys.exit(1)

def main():
    """Main launcher function"""
    print("🏥 GLASS Data Standardizer v2.0.0 - Production Ready")
    print("=" * 60)
    
    # Check Python version
    check_python_version()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    check_environment()
    
    # Setup production features
    logger = setup_logging()
    health_monitor = setup_health_monitoring()
    security_manager = setup_security()
    
    # Launch application
    launch_application()

if __name__ == "__main__":
    main()
