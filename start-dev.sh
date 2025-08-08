#!/bin/bash

# Development Start Script for Fishing Weather Portal

echo "🎣 Starting Fishing Weather Portal in Development Mode..."
echo "🌐 Portal will be available at: http://localhost:5000"
echo "📊 Database: SQLite (weather_data.db)"
echo "🔄 Press Ctrl+C to stop the server"

cd "$(dirname "$0")"
source venv/bin/activate
python3 app.py
