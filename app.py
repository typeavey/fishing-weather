#!/usr/bin/env python3
"""
Simple Fishing Weather API Server
Provides REST API endpoints for the fishing information portal
"""

import os
import json
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database paths
WEATHER_DB = "sqlite_db/weather_data.db"
STOCKING_DB = "sqlite_db/stocking_data.db"
WATER_TEMP_DB = "sqlite_db/water_temperature.db"

@app.route('/api/weather')
def get_weather():
    """Get weather data for all locations"""
    try:
        conn = sqlite3.connect(WEATHER_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM weather_data LIMIT 50")
        rows = cursor.fetchall()
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        # Convert to list of dictionaries
        weather_data = []
        for row in rows:
            weather_data.append(dict(zip(columns, row)))
        
        conn.close()
        return jsonify(weather_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stocking')
def get_stocking():
    """Get stocking data"""
    try:
        conn = sqlite3.connect(STOCKING_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM stocking_records LIMIT 50")
        rows = cursor.fetchall()
        
        columns = [description[0] for description in cursor.description]
        stocking_data = []
        for row in rows:
            stocking_data.append(dict(zip(columns, row)))
        
        conn.close()
        return jsonify(stocking_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/forecast')
def get_forecast():
    """Get weather forecast data"""
    try:
        conn = sqlite3.connect(WEATHER_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM weather_data WHERE date >= date('now') LIMIT 50")
        rows = cursor.fetchall()
        
        columns = [description[0] for description in cursor.description]
        forecast_data = []
        for row in rows:
            forecast_data.append(dict(zip(columns, row)))
        
        conn.close()
        return jsonify(forecast_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/locations')
def get_locations():
    """Get available fishing locations"""
    locations = [
        {"name": "Winnipesaukee", "lat": "43.6406", "lon": "-72.1440"},
        {"name": "Newfound", "lat": "43.7528", "lon": "-71.7999"},
        {"name": "Squam", "lat": "43.8280", "lon": "-71.5503"},
        {"name": "Champlain", "lat": "44.4896", "lon": "-73.3582"},
        {"name": "Mascoma", "lat": "43.6587", "lon": "-72.3200"},
        {"name": "Sunapee", "lat": "43.3770", "lon": "-72.0850"},
        {"name": "First Connecticut", "lat": "45.0926", "lon": "-71.2478"}
    ]
    return jsonify(locations)

@app.route('/')
def index():
    """Serve the main page"""
    return app.send_static_file('index.html')

if __name__ == '__main__':
    print("Starting Fishing Weather API Server...")
    app.run(host='0.0.0.0', port=5000, debug=False)
