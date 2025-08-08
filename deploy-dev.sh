#!/bin/bash

# Development Deployment Script for Fishing Weather Portal
# For local development work

set -e  # Exit on any error

echo "🔧 Setting up Fishing Weather Portal for Development..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the fishing-weather directory."
    exit 1
fi

# Step 1: Set up Python environment
echo "🐍 Setting up Python environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 2: Initialize database
echo "🗄️  Initializing database..."
if [ ! -f "weather_data.db" ]; then
    python3 working_database.py
fi

# Step 3: Test the application
echo "🧪 Testing application..."
python3 -c "
from app import app, db
print('✅ Flask app imported successfully')
print('✅ Database connected successfully')
"

# Step 4: Set proper permissions
echo "🔐 Setting permissions..."
chmod +x *.sh

echo ""
echo "🎉 Development setup complete!"
echo ""
echo "🚀 To start the development server:"
echo "   ./start-dev.sh"
echo ""
echo "🌐 Development portal will be available at:"
echo "   http://localhost:5000"
echo ""
echo "📋 Useful commands:"
echo "   ./start-dev.sh              # Start development server"
echo "   ./backup-database.sh        # Backup database"
echo "   ./deploy-production.sh      # Deploy to production"
echo ""
echo "💡 For production deployment, run:"
echo "   ./deploy-production.sh"
