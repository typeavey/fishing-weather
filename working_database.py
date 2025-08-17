#!/usr/bin/env python3
"""
Working SQLite Database for Fishing Weather Data
Matches existing database schema
"""

import sqlite3
import datetime
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class WorkingWeatherDatabase:
    def __init__(self, db_path: str = "sqlite_db/weather_data.db"):
        """Initialize SQLite database for weather data"""
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create weather_data table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS weather_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        location TEXT NOT NULL,
                        date_ts INTEGER,
                        date_str TEXT,
                        sunrise TEXT,
                        summary TEXT,
                        temp_day REAL,
                        pressure REAL,
                        wind_speed REAL,
                        wind_gust REAL,
                        fishing_base TEXT,
                        fishing_rating TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.info("Weather database tables initialized")
                
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
    
    def store_weather_data(self, weather_records: List[Dict[str, Any]]) -> bool:
        """Store weather data in the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for record in weather_records:
                    # Map current data structure to database schema
                    cursor.execute("""
                        INSERT OR REPLACE INTO weather_data (
                            location, date_ts, date_str, sunrise, summary,
                            temp_day, pressure, wind_speed, wind_gust, 
                            fishing_base, fishing_rating
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        record.get('location'),
                        int(record.get('date_ts').timestamp()) if record.get('date_ts') else None,
                        record.get('date_str'),
                        record.get('sunrise'),
                        record.get('summary'),
                        record.get('temp'),  # Map 'temp' to 'temp_day'
                        record.get('pressure'),
                        record.get('wind_speed'),
                        record.get('wind_gust'),
                        record.get('fishing_base'),
                        record.get('fishing_base')  # Use fishing_base for fishing_rating too
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

    def get_fishing_conditions(self, location: Optional[str] = None, 
                             days_back: int = 30) -> List[Dict[str, Any]]:
        """Get fishing conditions history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = """
                    SELECT location, date_str, fishing_base, wind_speed, wind_gust, 
                           temp_day as temperature, pressure
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

    def cleanup_old_data(self, days_to_keep: int = 30) -> int:
        """Remove weather data older than specified days"""
        try:
            cutoff_timestamp = int((datetime.datetime.now() - datetime.timedelta(days=days_to_keep)).timestamp())
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count records to be deleted
                cursor.execute("SELECT COUNT(*) FROM weather_data WHERE date_ts < ?", (cutoff_timestamp,))
                records_to_delete = cursor.fetchone()[0]
                
                if records_to_delete > 0:
                    # Delete old records
                    cursor.execute("DELETE FROM weather_data WHERE date_ts < ?", (cutoff_timestamp,))
                    conn.commit()
                    
                    logger.info(f"Cleaned up {records_to_delete} weather records older than {days_to_keep} days")
                    return records_to_delete
                else:
                    logger.info(f"No weather records older than {days_to_keep} days to clean up")
                    return 0
                    
        except Exception as e:
            logger.error(f"Error cleaning up old weather data: {e}")
            return 0

    def get_cleanup_statistics(self) -> Dict[str, Any]:
        """Get statistics about data that could be cleaned up"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count records older than 30 days
                cutoff_30 = int((datetime.datetime.now() - datetime.timedelta(days=30)).timestamp())
                cursor.execute("SELECT COUNT(*) FROM weather_data WHERE date_ts < ?", (cutoff_30,))
                older_than_30 = cursor.fetchone()[0]
                
                # Count records older than 60 days
                cutoff_60 = int((datetime.datetime.now() - datetime.timedelta(days=60)).timestamp())
                cursor.execute("SELECT COUNT(*) FROM weather_data WHERE date_ts < ?", (cutoff_60,))
                older_than_60 = cursor.fetchone()[0]
                
                # Count records older than 90 days
                cutoff_90 = int((datetime.datetime.now() - datetime.timedelta(days=90)).timestamp())
                cursor.execute("SELECT COUNT(*) FROM weather_data WHERE date_ts < ?", (cutoff_90,))
                older_than_90 = cursor.fetchone()[0]
                
                return {
                    'older_than_30_days': older_than_30,
                    'older_than_60_days': older_than_60,
                    'older_than_90_days': older_than_90,
                    'total_records': self.get_statistics().get('total_records', 0)
                }
                
        except Exception as e:
            logger.error(f"Error getting cleanup statistics: {e}")
            return {}

if __name__ == '__main__':
    # Example usage
    db = WorkingWeatherDatabase()
    
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
        'fishing_base': 'Good Fishing-Moderate Wind'
    }
    
    # Store data
    success = db.store_weather_data([sample_record])
    
    # Retrieve data
    data = db.get_weather_data(location='Winnipesaukee', limit=5)
    
    # Get statistics
    stats = db.get_statistics()
