#!/bin/bash

# Fishing Weather Portal - Production Start Script
# This script starts the fishing weather portal in production mode

echo "🎣 Starting Fishing Weather Portal (Production)..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the fishing-weather directory."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found. Please run deploy.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Set production environment variables
export FLASK_ENV=production
export FLASK_DEBUG=False
export PORT=5000

# Check if database exists
if [ ! -f "weather_data.db" ]; then
    echo "🗄️ Initializing SQLite database..."
    python3 working_database.py
fi

# Get server IP for display
SERVER_IP=$(hostname -I | awk '{print $1}' | head -n1)
if [ -z "$SERVER_IP" ]; then
    SERVER_IP="localhost"
fi

echo "🌐 Portal will be available at: http://$SERVER_IP:5000"
echo "📊 Database: SQLite (weather_data.db)"
echo "🔒 Production mode: Enabled"
echo "🔄 Press Ctrl+C to stop the server"
echo ""

# Start the application
python3 app.py
