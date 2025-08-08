#!/usr/bin/env python3
"""
PostgreSQL Database Implementation for Fishing Weather Data
Recommended for production use with larger datasets
"""

import psycopg2
import psycopg2.extras
import datetime
import json
import logging
from typing import Dict, List, Any, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class PostgreSQLWeatherDatabase:
    def __init__(self, connection_string: str = None, **kwargs):
        """
        Initialize PostgreSQL database connection
        
        Args:
            connection_string: Full connection string
            **kwargs: Individual connection parameters (host, port, database, user, password)
        """
        if connection_string:
            self.connection_string = connection_string
        else:
            # Build connection string from kwargs
            host = kwargs.get('host', 'localhost')
            port = kwargs.get('port', 5432)
            database = kwargs.get('database', 'fishing_weather')
            user = kwargs.get('user', 'postgres')
            password = kwargs.get('password', '')
            
            self.connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = psycopg2.connect(self.connection_string)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def init_database(self):
        """Create database tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Main weather data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weather_data (
                    id SERIAL PRIMARY KEY,
                    location VARCHAR(100) NOT NULL,
                    date_ts TIMESTAMP NOT NULL,
                    date_str VARCHAR(50) NOT NULL,
                    sunrise TIME,
                    sunset TIME,
                    summary TEXT,
                    
                    -- Temperature data
                    temp_day DECIMAL(5,2),
                    temp_min DECIMAL(5,2),
                    temp_max DECIMAL(5,2),
                    temp_night DECIMAL(5,2),
                    temp_eve DECIMAL(5,2),
                    temp_morn DECIMAL(5,2),
                    
                    -- Feels like temperature
                    feels_like_day DECIMAL(5,2),
                    feels_like_night DECIMAL(5,2),
                    feels_like_eve DECIMAL(5,2),
                    feels_like_morn DECIMAL(5,2),
                    
                    -- Atmospheric data
                    pressure DECIMAL(6,2),
                    humidity INTEGER,
                    dew_point DECIMAL(5,2),
                    
                    -- Wind data
                    wind_speed DECIMAL(5,2),
                    wind_deg INTEGER,
                    wind_gust DECIMAL(5,2),
                    
                    -- Astronomical data
                    moonrise TIMESTAMP,
                    moonset TIMESTAMP,
                    moon_phase DECIMAL(3,2),
                    
                    -- Cloud and UV data
                    clouds INTEGER,
                    uvi DECIMAL(4,2),
                    
                    -- Precipitation data
                    pop DECIMAL(3,2),
                    rain DECIMAL(6,2),
                    snow DECIMAL(6,2),
                    
                    -- Weather description
                    weather_id INTEGER,
                    weather_main VARCHAR(50),
                    weather_description VARCHAR(100),
                    weather_icon VARCHAR(10),
                    
                    -- Fishing analysis
                    fishing_base VARCHAR(100),
                    fishing_rating VARCHAR(100),
                    
                    -- Metadata
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    UNIQUE(location, date_ts)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_weather_location_date 
                ON weather_data(location, date_ts)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_weather_date_ts 
                ON weather_data(date_ts)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_weather_fishing_rating 
                ON weather_data(fishing_rating)
            """)
            
            # Locations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS locations (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    lat DECIMAL(10,6) NOT NULL,
                    lon DECIMAL(10,6) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Fishing conditions history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fishing_conditions (
                    id SERIAL PRIMARY KEY,
                    location VARCHAR(100) NOT NULL,
                    date_ts TIMESTAMP NOT NULL,
                    condition_type VARCHAR(50) NOT NULL,
                    wind_speed DECIMAL(5,2),
                    wind_gust DECIMAL(5,2),
                    temperature DECIMAL(5,2),
                    pressure DECIMAL(6,2),
                    humidity INTEGER,
                    moon_phase DECIMAL(3,2),
                    uvi DECIMAL(4,2),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Weather statistics table for caching
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weather_statistics (
                    id SERIAL PRIMARY KEY,
                    location VARCHAR(100) NOT NULL,
                    stat_date DATE NOT NULL,
                    avg_temp DECIMAL(5,2),
                    avg_wind_speed DECIMAL(5,2),
                    avg_pressure DECIMAL(6,2),
                    total_rain DECIMAL(6,2),
                    fishing_days INTEGER,
                    great_fishing_days INTEGER,
                    good_fishing_days INTEGER,
                    tough_fishing_days INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(location, stat_date)
                )
            """)
            
            conn.commit()
            logger.info("PostgreSQL database initialized successfully")
    
    def store_weather_data(self, weather_records: List[Dict[str, Any]]) -> bool:
        """Store weather data in the database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                for record in weather_records:
                    cursor.execute("""
                        INSERT INTO weather_data (
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
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        ) ON CONFLICT (location, date_ts) 
                        DO UPDATE SET
                            updated_at = CURRENT_TIMESTAMP,
                            temp_day = EXCLUDED.temp_day,
                            wind_speed = EXCLUDED.wind_speed,
                            fishing_rating = EXCLUDED.fishing_rating
                    """, (
                        record.get('location'),
                        record.get('date_ts'),
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
                        record.get('moonrise'),
                        record.get('moonset'),
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
                logger.info(f"Stored {len(weather_records)} weather records in PostgreSQL")
                return True
                
        except Exception as e:
            logger.error(f"Error storing weather data in PostgreSQL: {e}")
            return False
    
    def get_weather_data(self, location: Optional[str] = None,
                        start_date: Optional[datetime.datetime] = None,
                        end_date: Optional[datetime.datetime] = None,
                        limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve weather data from database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                
                query = "SELECT * FROM weather_data WHERE 1=1"
                params = []
                
                if location:
                    query += " AND location = %s"
                    params.append(location)
                
                if start_date:
                    query += " AND date_ts >= %s"
                    params.append(start_date)
                
                if end_date:
                    query += " AND date_ts <= %s"
                    params.append(end_date)
                
                query += " ORDER BY date_ts DESC LIMIT %s"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                result = []
                for row in rows:
                    row_dict = dict(row)
                    # Convert datetime objects to strings for JSON serialization
                    for key, value in row_dict.items():
                        if isinstance(value, datetime.datetime):
                            row_dict[key] = value.isoformat()
                        elif isinstance(value, datetime.time):
                            row_dict[key] = value.strftime('%H:%M')
                    result.append(row_dict)
                
                return result
                
        except Exception as e:
            logger.error(f"Error retrieving weather data from PostgreSQL: {e}")
            return []
    
    def get_fishing_conditions(self, location: Optional[str] = None,
                             days_back: int = 30) -> List[Dict[str, Any]]:
        """Get fishing conditions history"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                
                query = """
                    SELECT location, date_str, fishing_rating, wind_speed, wind_gust,
                           temp_day as temperature, pressure, humidity, moon_phase, uvi
                    FROM weather_data 
                    WHERE date_ts >= %s
                """
                params = [datetime.datetime.now() - datetime.timedelta(days=days_back)]
                
                if location:
                    query += " AND location = %s"
                    params.append(location)
                
                query += " ORDER BY date_ts DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error retrieving fishing conditions from PostgreSQL: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self.get_connection() as conn:
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
                        'start': min_date.isoformat() if min_date else None,
                        'end': max_date.isoformat() if max_date else None
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting statistics from PostgreSQL: {e}")
            return {}

if __name__ == "__main__":
    # Example usage
    print("PostgreSQL Weather Database Implementation")
    print("To use this, you'll need to:")
    print("1. Install PostgreSQL")
    print("2. Install psycopg2: pip install psycopg2-binary")
    print("3. Create a database")
    print("4. Update connection parameters")
