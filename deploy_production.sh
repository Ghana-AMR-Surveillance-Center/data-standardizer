#!/bin/bash

# GLASS Data Standardizer v2.0.0 - Production Deployment Script
# This script deploys the application in production mode

echo "============================================================"
echo "🏥 GLASS Data Standardizer v2.0.0 - Production Deployment"
echo "============================================================"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "✅ Python detected: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Install/upgrade dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs data config

# Set production environment variables
echo "⚙️ Setting production environment variables..."
export ENVIRONMENT=production
export SECRET_KEY="glass-prod-secret-key-2024"
export HOST=0.0.0.0
export PORT=8501
export LOG_LEVEL=INFO

# Validate configuration
echo "🔍 Validating configuration..."
python3 -c "from config.production import production_config; print('✅ Configuration valid' if production_config.validate_config() else '❌ Configuration invalid')"
if [ $? -ne 0 ]; then
    echo "❌ Configuration validation failed"
    exit 1
fi

# Start the application
echo
echo "🚀 Starting GLASS Data Standardizer in production mode..."
echo "📱 The application will be available at: http://localhost:8501"
echo "⏹️  Press Ctrl+C to stop the application"
echo

python3 run_production.py

echo
echo "👋 Application stopped"
