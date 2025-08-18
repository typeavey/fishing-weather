#!/usr/bin/env python3
"""
Weather Data Update Script
Fetches current weather data from OpenWeatherMap API and updates the database
"""

import os
import sys
import json
import time
import requests
import datetime
from typing import Dict, List, Any
from working_database import WorkingWeatherDatabase

# Add the website directory to Python path
website_dir = "/var/www/fishing.thepeaveys.net/public_html"
if website_dir not in sys.path:
    sys.path.insert(0, website_dir)

class WeatherDataUpdater:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        if not self.api_key:
            print("❌ OPENWEATHER_API_KEY environment variable not set")
            print("Please set your OpenWeatherMap API key:")
            print("export OPENWEATHER_API_KEY='your_api_key_here'")
            sys.exit(1)
        
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.locations = [
            {"name": "Winnipesaukee", "lat": 43.6406, "lon": -72.1440},
            {"name": "Newfound", "lat": 43.7528, "lon": -71.7999},
            {"name": "Squam", "lat": 43.8280, "lon": -71.5503},
            {"name": "Champlain", "lat": 44.4896, "lon": -73.3582},
            {"name": "Mascoma", "lat": 43.6587, "lon": -72.3200},
            {"name": "Sunapee", "lat": 43.3770, "lon": -72.0850},
            {"name": "First Connecticut", "lat": 45.0926, "lon": -71.2478}
        ]
        
        # Initialize database
        self.db = WorkingWeatherDatabase("../sqlite_db/weather_data.db")
        
    def get_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch current weather from OpenWeatherMap API"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'imperial'  # Use Fahrenheit
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant weather data
            weather_data = {
                'temp': data['main']['temp'],
                'pressure': data['main']['pressure'] / 33.8639,  # Convert hPa to inHg
                'wind_speed': data['wind']['speed'],
                'wind_gust': data['wind'].get('gust', data['wind']['speed']),
                'summary': data['weather'][0]['description'],
                'sunrise': datetime.datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M'),
                'created_at': datetime.datetime.now()
            }
            
            return weather_data
            
        except Exception as e:
            print(f"❌ Error fetching weather for {lat}, {lon}: {e}")
            return None
    
    def get_forecast_weather(self, lat: float, lon: float) -> List[Dict[str, Any]]:
        """Fetch 8-day forecast from OpenWeatherMap API"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'imperial',
                'cnt': 8  # 8 days
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            forecast_data = []
            
            for item in data['list']:
                # Get daily forecast (every 24 hours)
                if len(forecast_data) < 8:  # Limit to 8 days
                    weather_data = {
                        'temp': item['main']['temp'],
                        'pressure': item['main']['pressure'] / 33.8639,
                        'wind_speed': item['wind']['speed'],
                        'wind_gust': item['wind'].get('gust', item['wind']['speed']),
                        'summary': item['weather'][0]['description'],
                        'sunrise': 'N/A',  # Forecast API doesn't include sunrise data
                        'created_at': datetime.datetime.fromtimestamp(item['dt'])
                    }
                    forecast_data.append(weather_data)
            
            return forecast_data
            
        except Exception as e:
            print(f"❌ Error fetching forecast for {lat}, {lon}: {e}")
            return []
    
    def calculate_fishing_rating(self, wind_speed: float, temp: float, pressure: float) -> str:
        """Calculate fishing rating based on weather conditions"""
        # Wind speed is the most important factor (60% weight)
        if wind_speed <= 4:
            wind_score = 100
        elif wind_speed <= 6:
            wind_score = 80
        elif wind_speed <= 8:
            wind_score = 60
        elif wind_speed <= 10:
            wind_score = 40
        else:
            wind_score = 20
        
        # Temperature factor (15% weight)
        if 50 <= temp <= 75:
            temp_score = 100
        elif 40 <= temp <= 85:
            temp_score = 80
        else:
            temp_score = 60
        
        # Pressure factor (10% weight)
        if pressure < 29.8:
            pressure_score = 100  # Low pressure is good for fishing
        elif pressure <= 30.2:
            pressure_score = 80
        else:
            pressure_score = 60
        
        # Calculate weighted score
        total_score = (wind_score * 0.6) + (temp_score * 0.15) + (pressure_score * 0.1)
        
        # Convert to rating
        if total_score >= 90:
            return "Excellent Fishing"
        elif total_score >= 80:
            return "Great Fishing"
        elif total_score >= 70:
            return "Good Fishing"
        elif total_score >= 60:
            return "Fair Fishing"
        elif total_score >= 50:
            return "Moderate Fishing"
        else:
            return "Poor Fishing"
    
    def update_weather_data(self):
        """Update weather data for all locations"""
        print("🚀 Starting weather data update...")
        print(f"⏰ Update time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        total_updated = 0
        
        for location in self.locations:
            print(f"\n📍 Updating {location['name']}...")
            
            # Get current weather
            current_weather = self.get_current_weather(location['lat'], location['lon'])
            if current_weather:
                # Calculate fishing rating
                fishing_rating = self.calculate_fishing_rating(
                    current_weather['wind_speed'],
                    current_weather['temp'],
                    current_weather['pressure']
                )
                
                # Prepare record for database
                record = {
                    'location': location['name'],
                    'date_ts': current_weather['created_at'],
                    'date_str': current_weather['created_at'].strftime('%A %m-%d-%Y'),
                    'sunrise': current_weather['sunrise'],
                    'summary': current_weather['summary'],
                    'temp': current_weather['temp'],
                    'pressure': current_weather['pressure'],
                    'wind_speed': current_weather['wind_speed'],
                    'wind_gust': current_weather['wind_gust'],
                    'fishing_base': fishing_rating,
                    'fishing_rating': fishing_rating
                }
                
                # Store in database
                if self.db.store_weather_data([record]):
                    print(f"✅ Current weather updated: {fishing_rating}")
                    total_updated += 1
                else:
                    print("❌ Failed to store current weather")
            
            # Get forecast weather
            forecast_weather = self.get_forecast_weather(location['lat'], location['lon'])
            if forecast_weather:
                forecast_records = []
                for i, forecast in enumerate(forecast_weather):
                    # Calculate fishing rating for forecast
                    fishing_rating = self.calculate_fishing_rating(
                        forecast['wind_speed'],
                        forecast['temp'],
                        forecast['pressure']
                    )
                    
                    # Create forecast record
                    forecast_date = current_weather['created_at'] + datetime.timedelta(days=i+1)
                    record = {
                        'location': location['name'],
                        'date_ts': forecast_date,
                        'date_str': forecast_date.strftime('%A %m-%d-%Y'),
                        'sunrise': forecast['sunrise'],
                        'summary': forecast['summary'],
                        'temp': forecast['temp'],
                        'pressure': forecast['pressure'],
                        'wind_speed': forecast['wind_speed'],
                        'wind_gust': forecast['wind_gust'],
                        'fishing_base': fishing_rating,
                        'fishing_rating': fishing_rating
                    }
                    forecast_records.append(record)
                
                # Store forecast in database
                if self.db.store_weather_data(forecast_records):
                    print(f"✅ Forecast updated: {len(forecast_records)} days")
                    total_updated += len(forecast_records)
                else:
                    print("❌ Failed to store forecast")
            
            # Rate limiting to avoid API limits
            time.sleep(1)
        
        print("\n" + "=" * 60)
        print(f"🏁 Weather data update completed!")
        print(f"📊 Total records updated: {total_updated}")
        print(f"⏰ Completed at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return total_updated

def main():
    """Main function"""
    try:
        updater = WeatherDataUpdater()
        updater.update_weather_data()
    except KeyboardInterrupt:
        print("\n\n⏹️ Update interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error during update: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
