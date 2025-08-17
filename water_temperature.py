#!/usr/bin/env python3
"""
Water Temperature Data Module
Integrates USGS, NOAA, and estimation models for water temperature data
"""

import os
import json
import datetime
import logging
import requests
import sqlite3
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math

logger = logging.getLogger("water_temperature")

@dataclass
class WaterTemperatureRecord:
    """Represents a water temperature reading"""
    lake_name: str
    temperature_celsius: float
    temperature_fahrenheit: float
    timestamp: datetime.datetime
    source: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    depth: Optional[float] = None
    notes: str = ""

class WaterTemperatureData:
    """Handles water temperature data from multiple sources"""
    
    def __init__(self, db_path: str = "sqlite_db/water_temperature.db"):
        self.db_path = db_path
        
        # USGS site mappings for our lakes
        self.usgs_sites = {
            "Champlain": "04295000",  # RICHELIEU R (LAKE CHAMPLAIN) AT ROUSES POINT NY
            "Winnipesaukee": "01034500",  # LAKE WINNIPESAUKEE OUTLET AT LAKE VILLAGE NH
            "Newfound": "01076500",  # NEWFOUND RIVER AT BRISTOL NH
            "Squam": "01077500",  # SQUAM RIVER AT ASHLAND NH
            "Mascoma": "01158000",  # MASCOMA RIVER AT WEST LEBANON NH
            "Sunapee": "01078000",  # LAKE SUNAPEE OUTLET AT SUNAPEE NH
            "First Connecticut": "01144000",  # CONNECTICUT RIVER AT NORTH STRATFORD NH
        }
        
        # NOAA buoy mappings
        self.noaa_buoys = {
            "Champlain": "45012",  # Lake Champlain buoy
            "Winnipesaukee": None,  # No buoy available
        }
        
        # Lake characteristics for estimation
        self.lake_characteristics = {
            "Winnipesaukee": {"max_depth": 180, "avg_depth": 43, "surface_area": 71.8},
            "Newfound": {"max_depth": 183, "avg_depth": 45, "surface_area": 4.1},
            "Squam": {"max_depth": 99, "avg_depth": 25, "surface_area": 6.7},
            "Champlain": {"max_depth": 400, "avg_depth": 64, "surface_area": 490},
            "Mascoma": {"max_depth": 15, "avg_depth": 8, "surface_area": 0.8},
            "Sunapee": {"max_depth": 120, "avg_depth": 35, "surface_area": 6.5},
            "First Connecticut": {"max_depth": 20, "avg_depth": 10, "surface_area": 0.5},
        }
        
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize the water temperature database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS water_temperature_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lake_name TEXT NOT NULL,
                temperature_celsius REAL NOT NULL,
                temperature_fahrenheit REAL NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                source TEXT NOT NULL,
                latitude REAL,
                longitude REAL,
                depth REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS temperature_update_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                update_type TEXT NOT NULL,
                records_updated INTEGER DEFAULT 0,
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Water temperature database initialized")
    
    def fetch_usgs_temperature(self, lake_name: str) -> Optional[WaterTemperatureRecord]:
        """Fetch water temperature from USGS API"""
        site_id = self.usgs_sites.get(lake_name)
        if not site_id:
            return None
        
        try:
            url = f"https://waterservices.usgs.gov/nwis/iv/?format=json&sites={site_id}&parameterCd=00010"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse USGS response
                time_series = data.get('value', {}).get('timeSeries', [])
                if time_series:
                    series = time_series[0]
                    values = series.get('values', [{}])[0].get('value', [])
                    
                    if values:
                        latest = values[0]
                        temp_celsius = float(latest.get('value', 0))
                        temp_fahrenheit = (temp_celsius * 9/5) + 32
                        
                        # Parse timestamp
                        timestamp_str = latest.get('dateTime', '')
                        timestamp = datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        
                        # Get location info
                        source_info = series.get('sourceInfo', {})
                        geo_location = source_info.get('geoLocation', {}).get('geogLocation', {})
                        latitude = geo_location.get('latitude')
                        longitude = geo_location.get('longitude')
                        
                        return WaterTemperatureRecord(
                            lake_name=lake_name,
                            temperature_celsius=temp_celsius,
                            temperature_fahrenheit=temp_fahrenheit,
                            timestamp=timestamp,
                            source="USGS",
                            latitude=latitude,
                            longitude=longitude
                        )
            
        except Exception as e:
            logger.warning(f"Failed to fetch USGS data for {lake_name}: {e}")
        
        return None
    
    def fetch_noaa_temperature(self, lake_name: str) -> Optional[WaterTemperatureRecord]:
        """Fetch water temperature from NOAA buoy data"""
        buoy_id = self.noaa_buoys.get(lake_name)
        if not buoy_id:
            return None
        
        try:
            url = f"https://www.ndbc.noaa.gov/data/realtime2/{buoy_id}.txt"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                
                # Find the latest data line (skip header lines)
                for line in lines:
                    if line.startswith('2025') or line.startswith('2024'):  # Data line
                        parts = line.split()
                        if len(parts) >= 15:
                            # Parse NOAA format: YY MM DD hh mm WDIR WSPD GST WVHT DPD APD MWD PRES ATMP WTMP DEWP
                            try:
                                year = int(parts[0])
                                month = int(parts[1])
                                day = int(parts[2])
                                hour = int(parts[3])
                                minute = int(parts[4])
                                
                                # Water temperature is in column 14 (0-indexed)
                                temp_celsius = float(parts[13])
                                temp_fahrenheit = (temp_celsius * 9/5) + 32
                                
                                timestamp = datetime.datetime(year, month, day, hour, minute)
                                
                                return WaterTemperatureRecord(
                                    lake_name=lake_name,
                                    temperature_celsius=temp_celsius,
                                    temperature_fahrenheit=temp_fahrenheit,
                                    timestamp=timestamp,
                                    source="NOAA Buoy",
                                    notes=f"Buoy {buoy_id}"
                                )
                            except (ValueError, IndexError):
                                continue
                                break
            
        except Exception as e:
            logger.warning(f"Failed to fetch NOAA data for {lake_name}: {e}")
        
        return None
    
    def estimate_temperature(self, lake_name: str, air_temperature: float, date: datetime.date) -> WaterTemperatureRecord:
        """Estimate water temperature based on air temperature and seasonal patterns"""
        
        # Get lake characteristics
        lake_info = self.lake_characteristics.get(lake_name, {})
        max_depth = lake_info.get('max_depth', 50)
        avg_depth = lake_info.get('avg_depth', 25)
        
        # Seasonal adjustment factors
        day_of_year = date.timetuple().tm_yday
        
        # Seasonal temperature patterns for NH/VT lakes
        # Peak water temp typically occurs in August (day ~220)
        seasonal_factor = math.cos((day_of_year - 220) * 2 * math.pi / 365)
        
        # Lake-specific adjustments (more realistic for NH/VT lakes)
        lake_adjustments = {
            "Winnipesaukee": {"base_temp": 12, "seasonal_range": 10, "depth_factor": 0.8},  # Large, deep lake
            "Newfound": {"base_temp": 11, "seasonal_range": 9, "depth_factor": 0.7},        # Deep, clear lake
            "Squam": {"base_temp": 12, "seasonal_range": 10, "depth_factor": 0.8},          # Deep, clear lake
            "Champlain": {"base_temp": 14, "seasonal_range": 11, "depth_factor": 0.9},      # Large lake
            "Mascoma": {"base_temp": 13, "seasonal_range": 10, "depth_factor": 1.0},       # Smaller lake
            "Sunapee": {"base_temp": 11, "seasonal_range": 9, "depth_factor": 0.7},        # Deep, clear lake
            "First Connecticut": {"base_temp": 15, "seasonal_range": 12, "depth_factor": 1.1},  # River system
        }
        
        lake_adj = lake_adjustments.get(lake_name, {"base_temp": 15, "seasonal_range": 12, "depth_factor": 0.8})
        
        # Calculate estimated water temperature
        base_temp = lake_adj["base_temp"]
        seasonal_range = lake_adj["seasonal_range"]
        depth_factor = lake_adj["depth_factor"]
        
        # Seasonal component
        seasonal_temp = base_temp + (seasonal_range * seasonal_factor * 0.5)
        
        # Air temperature influence (lagged and dampened)
        air_influence = (air_temperature - 20) * 0.3 * depth_factor
        
        # Depth cooling effect
        depth_cooling = (max_depth / 100) * 2  # Deeper lakes are cooler
        
        estimated_celsius = seasonal_temp + air_influence - depth_cooling
        
        # Clamp to reasonable range
        estimated_celsius = max(0, min(30, estimated_celsius))
        estimated_fahrenheit = (estimated_celsius * 9/5) + 32
        
        return WaterTemperatureRecord(
            lake_name=lake_name,
            temperature_celsius=estimated_celsius,
            temperature_fahrenheit=estimated_fahrenheit,
            timestamp=datetime.datetime.now(),
            source="Estimation Model",
            depth=avg_depth,
            notes=f"Estimated based on air temp {air_temperature}°C, seasonal patterns, and lake characteristics"
        )
    
    def save_temperature_record(self, record: WaterTemperatureRecord) -> bool:
        """Save temperature record to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO water_temperature_records 
                (lake_name, temperature_celsius, temperature_fahrenheit, timestamp, source, latitude, longitude, depth, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.lake_name,
                record.temperature_celsius,
                record.temperature_fahrenheit,
                record.timestamp.isoformat(),
                record.source,
                record.latitude,
                record.longitude,
                record.depth,
                record.notes
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to save temperature record: {e}")
            return False
    
    def update_water_temperatures(self, air_temperatures: Dict[str, float] = None) -> Dict:
        """Update water temperature data for all lakes"""
        logger.info("Starting water temperature update")
        
        if air_temperatures is None:
            # Realistic August air temperatures for NH/VT lakes
            air_temperatures = {
                "Winnipesaukee": 24.0,  # ~75°F
                "Newfound": 23.5,       # ~74°F
                "Squam": 23.0,          # ~73°F
                "Champlain": 25.0,      # ~77°F
                "Mascoma": 24.5,        # ~76°F
                "Sunapee": 23.8,        # ~75°F
                "First Connecticut": 23.0, # ~73°F
            }
        
        records_updated = 0
        sources_used = []
        
        for lake_name in self.usgs_sites.keys():
            record = None
            
            # Try USGS first
            record = self.fetch_usgs_temperature(lake_name)
            if record:
                sources_used.append("USGS")
            else:
                # Try NOAA buoy
                record = self.fetch_noaa_temperature(lake_name)
                if record:
                    sources_used.append("NOAA")
                else:
                    # Use estimation model
                    air_temp = air_temperatures.get(lake_name, 25.0)  # Default to 25°C (~77°F)
                    record = self.estimate_temperature(lake_name, air_temp, datetime.date.today())
                    sources_used.append("Estimation")
            
            if record and self.save_temperature_record(record):
                records_updated += 1
        
        # Log update
        self.log_update("temperature_update", records_updated, True)
        
        return {
            'success': True,
            'records_updated': records_updated,
            'sources_used': sources_used
        }
    
    def log_update(self, update_type: str, records_updated: int, success: bool = True, error_message: str = None):
        """Log update activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO temperature_update_log (update_type, records_updated, success, error_message)
            VALUES (?, ?, ?, ?)
        ''', (update_type, records_updated, success, error_message))
        
        conn.commit()
        conn.close()
    
    def get_water_temperatures(self, lake_name: str = None, days_back: int = 7) -> List[Dict]:
        """Get water temperature data from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if lake_name:
            cursor.execute('''
                SELECT * FROM water_temperature_records 
                WHERE lake_name = ? 
                AND timestamp >= datetime('now', '-{} days')
                ORDER BY timestamp DESC
            '''.format(days_back), (lake_name,))
        else:
            cursor.execute('''
                SELECT * FROM water_temperature_records 
                WHERE timestamp >= datetime('now', '-{} days')
                ORDER BY timestamp DESC
            '''.format(days_back))
        
        records = cursor.fetchall()
        conn.close()
        
        # Convert to dictionary format
        result = []
        for record in records:
            result.append({
                'id': record[0],
                'lake_name': record[1],
                'temperature_celsius': record[2],
                'temperature_fahrenheit': record[3],
                'timestamp': record[4],
                'source': record[5],
                'latitude': record[6],
                'longitude': record[7],
                'depth': record[8],
                'notes': record[9],
                'created_at': record[10]
            })
        
        return result
    
    def get_latest_temperatures(self) -> Dict[str, Dict]:
        """Get latest water temperature for each lake"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT lake_name, temperature_celsius, temperature_fahrenheit, timestamp, source
            FROM water_temperature_records 
            WHERE id IN (
                SELECT MAX(id) 
                FROM water_temperature_records 
                GROUP BY lake_name
            )
            ORDER BY lake_name
        ''')
        
        records = cursor.fetchall()
        conn.close()
        
        result = {}
        for record in records:
            lake_name, temp_c, temp_f, timestamp, source = record
            result[lake_name] = {
                'temperature_celsius': temp_c,
                'temperature_fahrenheit': temp_f,
                'timestamp': timestamp,
                'source': source
            }
        
        return result

def main():
    """Test the water temperature module"""
    logging.basicConfig(level=logging.INFO)
    
    water_temp = WaterTemperatureData()
    
    # Test USGS data
    usgs_record = water_temp.fetch_usgs_temperature("Champlain")
    
    # Test NOAA data
    noaa_record = water_temp.fetch_noaa_temperature("Champlain")
    
    # Test estimation
    estimated = water_temp.estimate_temperature("Winnipesaukee", 22.0, datetime.date.today())
    
    # Update all temperatures
    result = water_temp.update_water_temperatures()
    
    # Get latest temperatures
    latest = water_temp.get_latest_temperatures()

if __name__ == "__main__":
    main()
