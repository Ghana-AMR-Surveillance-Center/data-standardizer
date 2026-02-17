#!/bin/bash

set -e

echo "🚀 AMR Data Harmonizer - Production Deployment"
echo "=================================================="

if [ "$EUID" -eq 0 ]; then 
   echo "❌ Please do not run as root"
   exit 1
fi

python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

echo "🔌 Activating virtual environment..."
source .venv/bin/activate

echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔍 Checking environment configuration..."
if [ -z "$ENVIRONMENT" ]; then
    echo "⚠️  ENVIRONMENT not set, defaulting to production"
    export ENVIRONMENT=production
fi

if [ -z "$SECRET_KEY" ]; then
    echo "⚠️  SECRET_KEY not set, generating one..."
    export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    echo "⚠️  Please set SECRET_KEY in your environment for production!"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs data

# Set permissions
chmod 755 logs data

# Run pre-deployment checks
echo "✅ Running pre-deployment checks..."
python3 -c "
import sys
from config.production import production_config
if not production_config.validate_config():
    print('⚠️  Configuration validation warnings (using defaults)')
    sys.exit(0)
"

# Start application
echo "🚀 Starting application..."
echo "=================================================="
python3 run_production.py
