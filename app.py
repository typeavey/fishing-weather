#!/usr/bin/env python3
"""
Fishing Weather API Server
Provides REST API endpoints for the fishing information portal
"""

import os
import json
import datetime
import logging
from flask import Flask, jsonify, request, send_from_directory

# Import CORS with fallback
try:
    from flask_cors import CORS
except ImportError:
    # Fallback for when flask-cors is not installed
    class CORS:
        def __init__(self, app):
            pass

# Import from the local fishing module
try:
    from fishing import (
        configure_logging,
        ensure_working_directory,
        load_config,
        load_settings,
        extract_thresholds,
        build_rows_for_location,
        group_rows_by_date
    )
except ImportError:
    # If running from a different directory, add the current directory to path
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from fishing import (
        configure_logging,
        ensure_working_directory,
        load_config,
        load_settings,
        extract_thresholds,
        build_rows_for_location,
        group_rows_by_date
    )

# Import database
try:
    from working_database import WorkingWeatherDatabase
except ImportError:
    # If running from a different directory, add the current directory to path
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from working_database import WorkingWeatherDatabase

# Import stocking data
try:
    from stocking_data import NHStockingData
except ImportError:
    # If running from a different directory, add the current directory to path
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from stocking_data import NHStockingData

# Import water temperature data
try:
    from water_temperature import WaterTemperatureData
except ImportError:
    # If running from a different directory, add the current directory to path
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from water_temperature import WaterTemperatureData

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
configure_logging()
logger = logging.getLogger("fishing_api")

# Global variables for caching
weather_cache = {}
cache_timestamp = None
CACHE_DURATION = 300  # 5 minutes

# Initialize database
db = WorkingWeatherDatabase()

# Initialize stocking data
stocking_data = NHStockingData()

# Initialize water temperature data
water_temp_data = WaterTemperatureData()

def get_cached_weather_data():
    """Get weather data from cache or database or generate new data"""
    global weather_cache, cache_timestamp
    
    current_time = datetime.datetime.now()
    
    # Check if cache is valid
    if (cache_timestamp and 
        (current_time - cache_timestamp).seconds < CACHE_DURATION and 
        weather_cache):
        logger.debug("Returning cached weather data")
        return weather_cache
    
    # Try to get data from database first
    try:
        logger.info("Attempting to load weather data from database")
        db_data = db.get_weather_data(limit=100)  # Get last 100 records
        if db_data:
            logger.info(f"Loaded {len(db_data)} records from database")
            # Convert database format to expected format
            weather_cache = []
            for record in db_data:
                # Convert database record to expected format
                weather_record = {
                    'date_ts': datetime.datetime.fromtimestamp(record['date_ts']) if record['date_ts'] else None,
                    'location': record['location'],
                    'date_str': record['date_str'],
                    'sunrise': record['sunrise'],
                    'summary': record['summary'],
                    'temp': record['temp_day'],
                    'pressure': record['pressure'],
                    'wind_speed': record['wind_speed'],
                    'wind_gust': record['wind_gust'],
                    'fishing': record['fishing_rating'] or record['fishing_base'],
                    'fishing_base': record['fishing_base']
                }
                weather_cache.append(weather_record)
            
            cache_timestamp = current_time
            return weather_cache
    except Exception as e:
        logger.warning(f"Failed to load data from database: {e}")
    
    # Generate new data if database is empty or failed
    logger.info("Generating new weather data")
    try:
        ensure_working_directory()
        api_key, output_dir = load_config()
        locations, thresholds_raw = load_settings()
        th = extract_thresholds(thresholds_raw)
        
        all_rows = []
        for location_name, coords in locations.items():
            rows = build_rows_for_location(location_name, coords, api_key, th)
            all_rows.extend(rows)
        
        # Store data in database
        if all_rows:
            try:
                db.store_weather_data(all_rows)
                logger.info(f"Stored {len(all_rows)} weather records in database")
            except Exception as e:
                logger.warning(f"Failed to store data in database: {e}")
        
        # Update cache
        weather_cache = all_rows
        cache_timestamp = current_time
        
        return all_rows
    except Exception as e:
        logger.error(f"Error generating weather data: {e}")
        return []

@app.route('/')
def index():
    """Serve the main portal page"""
    return send_from_directory('fishing-website', 'index.html')

@app.route('/weather-module')
def weather_module():
    """Serve the weather module page"""
    return send_from_directory('fishing-website', 'weather-module.html')

@app.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript files"""
    return send_from_directory('fishing-website/js', filename)

@app.route('/api/weather')
def api_weather():
    """API endpoint for weather data"""
    try:
        weather_data = get_cached_weather_data()
        return jsonify(weather_data)
    except Exception as e:
        logger.error(f"Error in /api/weather: {e}")
        return jsonify({"error": "Failed to fetch weather data"}), 500

@app.route('/api/forecast')
def api_forecast():
    """API endpoint for forecast data for a specific location"""
    try:
        location = request.args.get('location')
        if not location:
            return jsonify({"error": "Location parameter required"}), 400
        
        weather_data = get_cached_weather_data()
        location_data = [item for item in weather_data if item['location'] == location]
        
        if not location_data:
            return jsonify({"error": f"Location '{location}' not found"}), 404
        
        return jsonify(location_data)
    except Exception as e:
        logger.error(f"Error in /api/forecast: {e}")
        return jsonify({"error": "Failed to fetch forecast data"}), 500

@app.route('/api/locations')
def api_locations():
    """API endpoint for available locations"""
    try:
        ensure_working_directory()
        locations, _ = load_settings()
        return jsonify(list(locations.keys()))
    except Exception as e:
        logger.error(f"Error in /api/locations: {e}")
        return jsonify({"error": "Failed to fetch locations"}), 500

@app.route('/api/health')
def api_health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "cache_age": (datetime.datetime.now() - cache_timestamp).seconds if cache_timestamp else None,
        "database": "sqlite"
    })

@app.route('/api/weather/history')
def weather_history():
    """Get historical weather data from database"""
    try:
        location = request.args.get('location')
        days_back = int(request.args.get('days', 30))
        limit = int(request.args.get('limit', 100))
        
        start_date = datetime.datetime.now() - datetime.timedelta(days=days_back)
        
        data = db.get_weather_data(
            location=location,
            start_date=start_date,
            limit=limit
        )
        
        return jsonify({
            "data": data,
            "count": len(data),
            "location": location,
            "days_back": days_back
        })
    except Exception as e:
        logger.error(f"Error in /api/weather/history: {e}")
        return jsonify({"error": "Failed to fetch historical weather data"}), 500

@app.route('/api/weather/statistics')
def weather_statistics():
    """Get weather statistics from database"""
    try:
        stats = db.get_statistics()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error in /api/weather/statistics: {e}")
        return jsonify({"error": "Failed to fetch weather statistics"}), 500

@app.route('/api/fishing/conditions')
def fishing_conditions():
    """Get fishing conditions history"""
    try:
        location = request.args.get('location')
        days_back = int(request.args.get('days', 30))
        
        data = db.get_fishing_conditions(
            location=location,
            days_back=days_back
        )
        
        return jsonify({
            "data": data,
            "count": len(data),
            "location": location,
            "days_back": days_back
        })
    except Exception as e:
        logger.error(f"Error in /api/fishing/conditions: {e}")
        return jsonify({"error": "Failed to fetch fishing conditions"}), 500

@app.route('/api/stocking')
def api_stocking():
    """Get stocking data for all lakes"""
    try:
        lake_name = request.args.get('lake')
        days_back = int(request.args.get('days', 30))
        
        data = stocking_data.get_stocking_data(lake_name, days_back)
        return jsonify(data)
        
    except Exception as e:
        logger.error(f"Error in stocking API: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stocking/update')
def api_stocking_update():
    """Update stocking data from NH Fish & Game"""
    try:
        result = stocking_data.update_stocking_data()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in stocking update: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stocking/status')
def api_stocking_status():
    """Get stocking data update status"""
    try:
        status = stocking_data.get_update_status()
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error in stocking status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/water-temperature')
def api_water_temperature():
    """Get water temperature data for all lakes"""
    try:
        lake_name = request.args.get('lake')
        days_back = int(request.args.get('days', 7))
        
        data = water_temp_data.get_water_temperatures(lake_name, days_back)
        return jsonify(data)
        
    except Exception as e:
        logger.error(f"Error in water temperature API: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/water-temperature/latest')
def api_water_temperature_latest():
    """Get latest water temperature for each lake"""
    try:
        data = water_temp_data.get_latest_temperatures()
        return jsonify(data)
        
    except Exception as e:
        logger.error(f"Error in latest water temperature API: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/water-temperature/update')
def api_water_temperature_update():
    """Update water temperature data from USGS and NOAA"""
    try:
        result = water_temp_data.update_water_temperatures()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in water temperature update: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/weather-data.json')
def weather_data_json():
    """Serve weather data as JSON file (for static fallback)"""
    try:
        weather_data = get_cached_weather_data()
        return jsonify(weather_data)
    except Exception as e:
        logger.error(f"Error in /weather-data.json: {e}")
        return jsonify({"error": "Failed to fetch weather data"}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

@app.route('/weather.html')
def weather_page():
    """Serve the weather page"""
    return send_from_directory('fishing-website', 'weather.html')

@app.route('/locations.html')
def locations_page():
    """Serve the locations page"""
    return send_from_directory('fishing-website', 'locations.html')

@app.route('/forecast.html')
def forecast_page():
    """Serve the forecast page"""
    return send_from_directory('fishing-website', 'forecast.html')

@app.route('/analysis.html')
def analysis_page():
    """Serve the analysis page"""
    return send_from_directory('fishing-website', 'analysis.html')

@app.route('/guide.html')
def guide():
    """Serve the fishing analysis guide page"""
    return send_from_directory('fishing-website', 'guide.html')

@app.route('/stocking.html')
def stocking_page():
    """Serve the stocking page"""
    return send_from_directory('fishing-website', 'stocking.html')

@app.route('/demo.html')
def demo_page():
    """Serve the demo page"""
    return send_from_directory('fishing-website', 'demo.html')

if __name__ == '__main__':
    # Load initial data
    logger.info("Starting Fishing Weather API Server")
    get_cached_weather_data()
    
    # Check if running in production
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=debug_mode,
        threaded=True  # Enable threading for production
    )
