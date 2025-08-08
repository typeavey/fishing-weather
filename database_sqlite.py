#!/usr/bin/env python3
"""
SQLite Database Implementation for Fishing Weather Data
Perfect for small to medium-scale weather data storage
"""

import sqlite3
import datetime
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class WeatherDatabase:
    def __init__(self, db_path: str = "weather_data.db"):
        """Initialize SQLite database for weather data"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Main weather data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weather_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    location TEXT NOT NULL,
                    date_ts INTEGER NOT NULL,
                    date_str TEXT NOT NULL,
                    sunrise TEXT,
                    sunset TEXT,
                    summary TEXT,
                    
                    -- Temperature data
                    temp_day REAL,
                    temp_min REAL,
                    temp_max REAL,
                    temp_night REAL,
                    temp_eve REAL,
                    temp_morn REAL,
                    
                    -- Feels like temperature
                    feels_like_day REAL,
                    feels_like_night REAL,
                    feels_like_eve REAL,
                    feels_like_morn REAL,
                    
                    -- Atmospheric data
                    pressure REAL,
                    humidity INTEGER,
                    dew_point REAL,
                    
                    -- Wind data
                    wind_speed REAL,
                    wind_deg INTEGER,
                    wind_gust REAL,
                    
                    -- Astronomical data
                    moonrise INTEGER,
                    moonset INTEGER,
                    moon_phase REAL,
                    
                    -- Cloud and UV data
                    clouds INTEGER,
                    uvi REAL,
                    
                    -- Precipitation data
                    pop REAL,
                    rain REAL,
                    snow REAL,
                    
                    -- Weather description
                    weather_id INTEGER,
                    weather_main TEXT,
                    weather_description TEXT,
                    weather_icon TEXT,
                    
                    -- Fishing analysis
                    fishing_base TEXT,
                    fishing_rating TEXT,
                    
                    -- Metadata
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    UNIQUE(location, date_ts)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_location_date ON weather_data(location, date_ts)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_date_ts ON weather_data(date_ts)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_fishing_rating ON weather_data(fishing_rating)")
            
            # Locations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    lat REAL NOT NULL,
                    lon REAL NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Fishing conditions history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fishing_conditions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    location TEXT NOT NULL,
                    date_ts INTEGER NOT NULL,
                    condition_type TEXT NOT NULL,
                    wind_speed REAL,
                    wind_gust REAL,
                    temperature REAL,
                    pressure REAL,
                    humidity INTEGER,
                    moon_phase REAL,
                    uvi REAL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            logger.info(f"Database initialized: {self.db_path}")
    
    def store_weather_data(self, weather_records: List[Dict[str, Any]]) -> bool:
        """Store weather data in the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for record in weather_records:
                    cursor.execute("""
                        INSERT OR REPLACE INTO weather_data (
                            location, date_ts, date_str, sunrise, sunset, summary,
                            temp_day, temp_min, temp_max, temp_night, temp_eve, temp_morn,
                            feels_like_day, feels_like_night, feels_like_eve, feels_like_morn,
                            pressure, humidity, dew_point,
                            wind_speed, wind_deg, wind_gust,
                            moonrise, moonset, moon_phase,
                            clouds, uvi,
                            pop, rain, snow,
                            weather_id, weather_main, weather_description, weather_icon,
                            fishing_base, fishing_rating
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        record.get('location'),
                        int(record.get('date_ts').timestamp()) if record.get('date_ts') else None,
                        record.get('date_str'),
                        record.get('sunrise'),
                        record.get('sunset'),
                        record.get('summary'),
                        record.get('temp_day'),
                        record.get('temp_min'),
                        record.get('temp_max'),
                        record.get('temp_night'),
                        record.get('temp_eve'),
                        record.get('temp_morn'),
                        record.get('feels_like_day'),
                        record.get('feels_like_night'),
                        record.get('feels_like_eve'),
                        record.get('feels_like_morn'),
                        record.get('pressure'),
                        record.get('humidity'),
                        record.get('dew_point'),
                        record.get('wind_speed'),
                        record.get('wind_deg'),
                        record.get('wind_gust'),
                        int(record.get('moonrise').timestamp()) if record.get('moonrise') else None,
                        int(record.get('moonset').timestamp()) if record.get('moonset') else None,
                        record.get('moon_phase'),
                        record.get('clouds'),
                        record.get('uvi'),
                        record.get('pop'),
                        record.get('rain'),
                        record.get('snow'),
                        record.get('weather_id'),
                        record.get('weather_main'),
                        record.get('weather_description'),
                        record.get('weather_icon'),
                        record.get('fishing_base'),
                        record.get('fishing_rating')
                    ))
                
                conn.commit()
                logger.info(f"Stored {len(weather_records)} weather records")
                return True
                
        except Exception as e:
            logger.error(f"Error storing weather data: {e}")
            return False
    
    def get_weather_data(self, location: Optional[str] = None, 
                        start_date: Optional[datetime.datetime] = None,
                        end_date: Optional[datetime.datetime] = None,
                        limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve weather data from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Enable column access by name
                cursor = conn.cursor()
                
                query = "SELECT * FROM weather_data WHERE 1=1"
                params = []
                
                if location:
                    query += " AND location = ?"
                    params.append(location)
                
                if start_date:
                    query += " AND date_ts >= ?"
                    params.append(int(start_date.timestamp()))
                
                if end_date:
                    query += " AND date_ts <= ?"
                    params.append(int(end_date.timestamp()))
                
                query += " ORDER BY date_ts DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                result = []
                for row in rows:
                    row_dict = dict(row)
                    # Convert timestamps back to datetime objects
                    if row_dict.get('date_ts'):
                        row_dict['date_ts'] = datetime.datetime.fromtimestamp(row_dict['date_ts'])
                    if row_dict.get('moonrise'):
                        row_dict['moonrise'] = datetime.datetime.fromtimestamp(row_dict['moonrise'])
                    if row_dict.get('moonset'):
                        row_dict['moonset'] = datetime.datetime.fromtimestamp(row_dict['moonset'])
                    result.append(row_dict)
                
                return result
                
        except Exception as e:
            logger.error(f"Error retrieving weather data: {e}")
            return []
    
    def get_fishing_conditions(self, location: Optional[str] = None, 
                             days_back: int = 30) -> List[Dict[str, Any]]:
        """Get fishing conditions history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = """
                    SELECT location, date_str, fishing_rating, wind_speed, wind_gust, 
                           temperature, pressure, humidity, moon_phase, uvi
                    FROM weather_data 
                    WHERE date_ts >= ?
                """
                params = [int((datetime.datetime.now() - datetime.timedelta(days=days_back)).timestamp())]
                
                if location:
                    query += " AND location = ?"
                    params.append(location)
                
                query += " ORDER BY date_ts DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error retrieving fishing conditions: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total records
                cursor.execute("SELECT COUNT(*) FROM weather_data")
                total_records = cursor.fetchone()[0]
                
                # Records by location
                cursor.execute("SELECT location, COUNT(*) FROM weather_data GROUP BY location")
                location_counts = dict(cursor.fetchall())
                
                # Date range
                cursor.execute("SELECT MIN(date_ts), MAX(date_ts) FROM weather_data")
                min_date, max_date = cursor.fetchone()
                
                return {
                    'total_records': total_records,
                    'location_counts': location_counts,
                    'date_range': {
                        'start': datetime.datetime.fromtimestamp(min_date) if min_date else None,
                        'end': datetime.datetime.fromtimestamp(max_date) if max_date else None
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}

if __name__ == "__main__":
    # Example usage
    db = WeatherDatabase()
    
    # Example weather record
    sample_record = {
        'location': 'Winnipesaukee',
        'date_ts': datetime.datetime.now(),
        'date_str': 'Friday 08-08-2025',
        'temp_day': 65.0,
        'wind_speed': 8.5,
        'fishing_rating': 'Good Fishing'
    }
    
    # Store data
    success = db.store_weather_data([sample_record])
    print(f"Data stored: {success}")
    
    # Retrieve data
    data = db.get_weather_data(location='Winnipesaukee', limit=5)
    print(f"Retrieved {len(data)} records")
    
    # Get statistics
    stats = db.get_statistics()
    print(f"Database statistics: {stats}")
