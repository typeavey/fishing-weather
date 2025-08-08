#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
echo "🎣 Starting Fishing Weather Portal..."
echo "🌐 Portal will be available at: http://localhost:5000"
echo "📊 Database: SQLite (weather_data.db)"
echo "🔄 Press Ctrl+C to stop the server"
python3 app.py
