#!/usr/bin/env python3
"""
Simple Fishing Weather API Server
Provides REST API endpoints for the fishing information portal
"""

import os
import json
import sqlite3
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS

# Add scripts directory to Python path for working_database import
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

app = Flask(__name__)
CORS(app)

# Database paths
WEATHER_DB = "sqlite_db/weather_data.db"
STOCKING_DB = "sqlite_db/stocking_data.db"
WATER_TEMP_DB = "sqlite_db/water_temperature.db"

def cleanup_old_weather_data():
    """Clean up weather data older than 30 days"""
    try:
        from working_database import WorkingWeatherDatabase
        db = WorkingWeatherDatabase()
        deleted_count = db.cleanup_old_data(days_to_keep=30)
        if deleted_count > 0:
            print(f"Cleaned up {deleted_count} old weather records")
        return deleted_count
    except Exception as e:
        print(f"Error during cleanup: {e}")
        return 0

# Run cleanup on startup
cleanup_old_weather_data()

@app.route('/api/weather')
def get_weather():
    """Get weather data for all locations"""
    try:
        conn = sqlite3.connect(WEATHER_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM weather_data ORDER BY created_at DESC LIMIT 50")
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

@app.route('/api/water-temperature')
def get_water_temperature():
    """Get water temperature data"""
    try:
        conn = sqlite3.connect(WATER_TEMP_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM water_temperature_records ORDER BY timestamp DESC LIMIT 50")
        rows = cursor.fetchall()
        
        columns = [description[0] for description in cursor.description]
        water_temp_data = []
        for row in rows:
            water_temp_data.append(dict(zip(columns, row)))
        
        conn.close()
        return jsonify(water_temp_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/water-temperature/latest')
def get_latest_water_temperature():
    """Get latest water temperature data for each lake"""
    try:
        conn = sqlite3.connect(WATER_TEMP_DB)
        cursor = conn.cursor()
        
        # Get the latest temperature for each lake
        cursor.execute("""
            SELECT lake_name, temperature_celsius, temperature_fahrenheit, 
                   timestamp, source, latitude, longitude, depth, notes
            FROM water_temperature_records w1
            WHERE timestamp = (
                SELECT MAX(timestamp) 
                FROM water_temperature_records w2 
                WHERE w2.lake_name = w1.lake_name
            )
            ORDER BY lake_name
        """)
        
        rows = cursor.fetchall()
        
        # Convert to dictionary format expected by frontend
        latest_data = {}
        for row in rows:
            lake_name = row[0]
            latest_data[lake_name] = {
                'temperature_celsius': row[1],
                'temperature_fahrenheit': row[2],
                'timestamp': row[3],
                'source': row[4],
                'latitude': row[5],
                'longitude': row[6],
                'depth': row[7],
                'notes': row[8]
            }
        
        conn.close()
        return jsonify(latest_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/forecast')
def get_forecast():
    """Get weather forecast data"""
    try:
        conn = sqlite3.connect(WEATHER_DB)
        cursor = conn.cursor()
        # Use date_ts (timestamp) instead of non-existent date column
        # Get current timestamp and data from last 8 days (forecast period)
        import time
        current_timestamp = int(time.time())
        eight_days_ago = current_timestamp - (8 * 24 * 60 * 60)  # 8 days ago
        
        cursor.execute("SELECT * FROM weather_data WHERE date_ts >= ? ORDER BY date_ts DESC LIMIT 50", (eight_days_ago,))
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

@app.route('/api/cleanup', methods=['POST'])
def trigger_cleanup():
    """Manually trigger cleanup of old weather data"""
    try:
        days_to_keep = request.json.get('days_to_keep', 30) if request.json else 30
        deleted_count = cleanup_old_weather_data()
        
        # Get cleanup statistics
        from working_database import WorkingWeatherDatabase
        db = WorkingWeatherDatabase()
        cleanup_stats = db.get_cleanup_statistics()
        
        return jsonify({
            "success": True,
            "deleted_records": deleted_count,
            "cleanup_stats": cleanup_stats,
            "message": f"Cleanup completed. Kept data from last {days_to_keep} days."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cleanup/stats')
def get_cleanup_stats():
    """Get cleanup statistics"""
    try:
        from working_database import WorkingWeatherDatabase
        db = WorkingWeatherDatabase()
        cleanup_stats = db.get_cleanup_statistics()
        return jsonify(cleanup_stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

from flask import send_file

@app.route('/')
def index():
    """Serve the main page"""
    return send_file('index.html')

@app.route('/weather.html')
def weather():
    """Serve the weather page"""
    return send_file('weather.html')

@app.route('/forecast.html')
def forecast():
    """Serve the forecast page"""
    return send_file('forecast.html')

@app.route('/locations.html')
def locations():
    """Serve the locations page"""
    return send_file('locations.html')

@app.route('/stocking.html')
def stocking():
    """Serve the stocking page"""
    return send_file('stocking.html')

@app.route('/analysis.html')
def analysis():
    """Serve the analysis page"""
    return send_file('analysis.html')

@app.route('/guide.html')
def guide():
    """Serve the guide page"""
    return send_file('guide.html')

@app.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript files"""
    return send_file(f'js/{filename}')

@app.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS files"""
    return send_file(f'css/{filename}')

@app.route('/debug_weather.html')
def debug_weather():
    """Serve the weather debug page"""
    return send_file('debug_weather.html')







if __name__ == '__main__':
    print("Starting Fishing Weather API Server...")
    app.run(host='0.0.0.0', port=5000, debug=False)
