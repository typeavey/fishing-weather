#!/bin/bash

# Fishing Information Portal Startup Script

echo "🎣 Starting Fishing Information Portal..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if config.json exists
if [ ! -f "config.json" ]; then
    echo "⚠️  Warning: config.json not found!"
    echo "Please create config.json with your OpenWeatherMap API key:"
    echo '{
  "api_key": "your_api_key_here",
  "output_dir": "./fishing-website"
}'
    exit 1
fi

# Start the Flask server
echo "🚀 Starting Flask API server..."
echo "Portal will be available at: http://localhost:5000"
echo "Weather Module: http://localhost:5000/weather-module"
echo "Weather Widget: http://localhost:5000/weather-widget"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
