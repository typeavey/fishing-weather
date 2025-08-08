#!/usr/bin/env python3
"""
Simple SQLite Database for Fishing Weather Data
Compatible with current weather data structure
"""

import sqlite3
import datetime
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class SimpleWeatherDatabase:
    def __init__(self, db_path: str = "weather_data.db"):
        """Initialize SQLite database for weather data"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Main weather data table - matches current data structure
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weather_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    location TEXT NOT NULL,
                    date_ts INTEGER NOT NULL,
                    date_str TEXT NOT NULL,
                    sunrise TEXT,
                    summary TEXT,
                    temp REAL,
                    pressure REAL,
                    wind_speed REAL,
                    wind_gust REAL,
                    fishing TEXT,
                    fishing_base TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(location, date_ts)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_location_date ON weather_data(location, date_ts)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_date_ts ON weather_data(date_ts)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_fishing_base ON weather_data(fishing_base)")
            
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
                            location, date_ts, date_str, sunrise, summary,
                            temp, pressure, wind_speed, wind_gust, fishing, fishing_base
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        record.get('location'),
                        int(record.get('date_ts').timestamp()) if record.get('date_ts') else None,
                        record.get('date_str'),
                        record.get('sunrise'),
                        record.get('summary'),
                        record.get('temp'),
                        record.get('pressure'),
                        record.get('wind_speed'),
                        record.get('wind_gust'),
                        record.get('fishing'),
                        record.get('fishing_base')
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
                conn.row_factory = sqlite3.Row
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
                    SELECT location, date_str, fishing_base, wind_speed, wind_gust, 
                           temp as temperature, pressure
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

if __name__ == '__main__':
    # Example usage
    db = SimpleWeatherDatabase()
    
    # Example weather record matching current structure
    sample_record = {
        'location': 'Winnipesaukee',
        'date_ts': datetime.datetime.now(),
        'date_str': 'Friday 08-08-2025',
        'sunrise': '06:30',
        'summary': 'Clear sky',
        'temp': 65.0,
        'pressure': 29.92,
        'wind_speed': 8.5,
        'wind_gust': 12.0,
        'fishing': 'Good Fishing (Comfortable Temp, High Pressure)',
        'fishing_base': 'Good Fishing-Moderate Wind'
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
