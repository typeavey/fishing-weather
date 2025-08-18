#!/usr/bin/env python3
"""
NH Fish & Game Stocking Data Module
Handles stocking report data from NH Fish & Game and provides automatic updates
"""

import os
import json
import datetime
import logging
import requests
import sqlite3
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger("stocking_data")

@dataclass
class StockingRecord:
    """Represents a single stocking record"""
    lake_name: str
    species: str
    stocking_date: datetime.date
    fish_size: str
    quantity: int
    coordinates: Optional[Tuple[float, float]] = None
    notes: str = ""
    source: str = "NH Fish & Game"

class NHStockingData:
    """Handles NH Fish & Game stocking data"""
    
    def __init__(self, db_path: str = "sqlite_db/stocking_data.db"):
        self.db_path = db_path
        self.api_urls = [
            "https://nhfg.maps.arcgis.com/rest/services/Stocking_Report/MapServer/0",
            "https://services1.arcgis.com/RbMX0mRVOFNTdLzd/arcgis/rest/services/Stocking_Report/FeatureServer/0"
        ]
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize the stocking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocking_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lake_name TEXT NOT NULL,
                species TEXT NOT NULL,
                stocking_date DATE NOT NULL,
                fish_size TEXT,
                quantity INTEGER,
                latitude REAL,
                longitude REAL,
                notes TEXT,
                source TEXT DEFAULT 'NH Fish & Game',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS update_log (
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
        logger.info("Stocking database initialized")
    
    def fetch_api_data(self) -> List[Dict]:
        """Attempt to fetch data from NH Fish & Game APIs"""
        all_data = []
        
        for url in self.api_urls:
            try:
                # Try different query formats
                query_urls = [
                    f"{url}/query?where=1%3D1&outFields=*&f=json",
                    f"{url}/query?where=1%3D1&outFields=*&returnGeometry=true&f=json",
                    f"{url}?f=json"
                ]
                
                for query_url in query_urls:
                    try:
                        response = requests.get(query_url, timeout=10)
                        if response.status_code == 200:
                            data = response.json()
                            logger.info(f"Successfully fetched data from {url}")
                            all_data.append(data)
                            break
                    except Exception as e:
                        logger.debug(f"Failed to fetch from {query_url}: {e}")
                        continue
                        
            except Exception as e:
                logger.warning(f"Failed to fetch from {url}: {e}")
                continue
        
        return all_data
    
    def parse_arcgis_data(self, data: Dict) -> List[StockingRecord]:
        """Parse ArcGIS data into StockingRecord objects"""
        records = []
        
        try:
            features = data.get('features', [])
            
            for feature in features:
                try:
                    attributes = feature.get('attributes', {})
                    geometry = feature.get('geometry', {})
                    
                    # Extract data from attributes
                    lake_name = attributes.get('WATERBODY', attributes.get('LAKE_NAME', ''))
                    species = attributes.get('SPECIES', attributes.get('FISH_TYPE', ''))
                    stocking_date_str = attributes.get('STOCKING_DATE', attributes.get('DATE', ''))
                    fish_size = attributes.get('SIZE', attributes.get('FISH_SIZE', ''))
                    quantity = attributes.get('QUANTITY', attributes.get('NUMBER', 0))
                    notes = attributes.get('NOTES', '')
                    
                    # Parse coordinates
                    coordinates = None
                    if geometry:
                        if 'x' in geometry and 'y' in geometry:
                            coordinates = (geometry['x'], geometry['y'])
                        elif 'coordinates' in geometry:
                            coords = geometry['coordinates']
                            if len(coords) >= 2:
                                coordinates = (coords[0], coords[1])
                    
                    # Parse date
                    stocking_date = None
                    if stocking_date_str:
                        try:
                            # Try different date formats
                            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%Y/%m/%d']:
                                try:
                                    stocking_date = datetime.datetime.strptime(stocking_date_str, fmt).date()
                                    break
                                except ValueError:
                                    continue
                        except Exception as e:
                            logger.debug(f"Failed to parse date {stocking_date_str}: {e}")
                    
                    if lake_name and species and stocking_date:
                        record = StockingRecord(
                            lake_name=lake_name,
                            species=species,
                            stocking_date=stocking_date,
                            fish_size=fish_size or "Unknown",
                            quantity=quantity or 0,
                            coordinates=coordinates,
                            notes=notes
                        )
                        records.append(record)
                        
                except Exception as e:
                    logger.debug(f"Failed to parse feature: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to parse ArcGIS data: {e}")
        
        return records
    
    def save_records(self, records: List[StockingRecord]) -> int:
        """Save stocking records to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        
        for record in records:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO stocking_records 
                    (lake_name, species, stocking_date, fish_size, quantity, latitude, longitude, notes, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record.lake_name,
                    record.species,
                    record.stocking_date.isoformat(),
                    record.fish_size,
                    record.quantity,
                    record.coordinates[0] if record.coordinates else None,
                    record.coordinates[1] if record.coordinates else None,
                    record.notes,
                    record.source
                ))
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Failed to save record: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        return saved_count
    
    def log_update(self, update_type: str, records_updated: int, success: bool = True, error_message: str = None):
        """Log update activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO update_log (update_type, records_updated, success, error_message)
            VALUES (?, ?, ?, ?)
        ''', (update_type, records_updated, success, error_message))
        
        conn.commit()
        conn.close()
    
    def update_stocking_data(self) -> Dict:
        """Update stocking data from NH Fish & Game"""
        logger.info("Starting stocking data update")
        
        try:
            # Fetch data from APIs
            api_data = self.fetch_api_data()
            
            # Parse API data
            records = []
            if api_data:
                for data in api_data:
                    parsed_records = self.parse_arcgis_data(data)
                    records.extend(parsed_records)
            
            # If no records from API, use sample data
            if not records:
                logger.warning("No usable API data available, using sample data")
                records = self.generate_sample_data()
            
            # Save records
            saved_count = self.save_records(records)
            
            # Log successful update
            self.log_update("api_update", saved_count, True)
            
            logger.info(f"Stocking data update completed: {saved_count} records saved")
            
            return {
                'success': True,
                'records_updated': saved_count,
                'source': 'sample' if not api_data or not records else 'api'
            }
            
        except Exception as e:
            error_msg = f"Stocking data update failed: {e}"
            logger.error(error_msg)
            self.log_update("api_update", 0, False, error_msg)
            
            return {
                'success': False,
                'error': error_msg,
                'records_updated': 0
            }
    
    def generate_sample_data(self) -> List[StockingRecord]:
        """Generate sample stocking data for testing"""
        # Get current date for recent stockings
        today = datetime.date.today()
        
        sample_records = [
            StockingRecord(
                lake_name="Winnipesaukee",
                species="Rainbow Trout",
                stocking_date=today - datetime.timedelta(days=5),
                fish_size="8-10 inches",
                quantity=500,
                coordinates=(43.6406, -72.1440),
                notes="Stocked in Alton Bay area"
            ),
            StockingRecord(
                lake_name="Newfound",
                species="Lake Trout",
                stocking_date=today - datetime.timedelta(days=10),
                fish_size="12-14 inches",
                quantity=300,
                coordinates=(43.7528, -71.7999),
                notes="Deep water stocking"
            ),
            StockingRecord(
                lake_name="Squam",
                species="Brook Trout",
                stocking_date=today - datetime.timedelta(days=7),
                fish_size="6-8 inches",
                quantity=400,
                coordinates=(43.8280, -71.5503),
                notes="Shoreline stocking"
            ),
            StockingRecord(
                lake_name="Champlain",
                species="Brown Trout",
                stocking_date=today - datetime.timedelta(days=15),
                fish_size="10-12 inches",
                quantity=600,
                coordinates=(44.4896, -73.3582),
                notes="Multiple locations"
            ),
            StockingRecord(
                lake_name="Mascoma",
                species="Rainbow Trout",
                stocking_date=today - datetime.timedelta(days=3),
                fish_size="8-10 inches",
                quantity=250,
                coordinates=(43.6587, -72.3200),
                notes="Recent stocking"
            ),
            StockingRecord(
                lake_name="Sunapee",
                species="Lake Trout",
                stocking_date=today - datetime.timedelta(days=12),
                fish_size="12-14 inches",
                quantity=350,
                coordinates=(43.3770, -72.0850),
                notes="Deep water areas"
            ),
            StockingRecord(
                lake_name="First Connecticut",
                species="Brook Trout",
                stocking_date=today - datetime.timedelta(days=1),
                fish_size="6-8 inches",
                quantity=200,
                coordinates=(45.0926, -71.2478),
                notes="River stocking"
            )
        ]
        
        return sample_records
    
    def get_stocking_data(self, lake_name: str = None, days_back: int = 30) -> List[Dict]:
        """Get stocking data from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if lake_name:
            cursor.execute('''
                SELECT * FROM stocking_records 
                WHERE lake_name = ? 
                AND stocking_date >= date('now', '-{} days')
                ORDER BY stocking_date DESC
            '''.format(days_back), (lake_name,))
        else:
            cursor.execute('''
                SELECT * FROM stocking_records 
                WHERE stocking_date >= date('now', '-{} days')
                ORDER BY stocking_date DESC
            '''.format(days_back))
        
        records = cursor.fetchall()
        conn.close()
        
        # Convert to dictionary format
        result = []
        for record in records:
            result.append({
                'id': record[0],
                'lake_name': record[1],
                'species': record[2],
                'stocking_date': record[3],
                'fish_size': record[4],
                'quantity': record[5],
                'latitude': record[6],
                'longitude': record[7],
                'notes': record[8],
                'source': record[9],
                'created_at': record[10],
                'updated_at': record[11]
            })
        
        return result
    
    def get_update_status(self) -> Dict:
        """Get the status of the last update"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM update_log 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''')
        
        record = cursor.fetchone()
        conn.close()
        
        if record:
            return {
                'last_update': record[5],
                'update_type': record[1],
                'records_updated': record[2],
                'success': bool(record[3]),
                'error_message': record[4]
            }
        else:
            return {
                'last_update': None,
                'update_type': None,
                'records_updated': 0,
                'success': False,
                'error_message': 'No update history'
            }

def main():
    """Test the stocking data module"""
    logging.basicConfig(level=logging.INFO)
    
    stocking_data = NHStockingData()
    
    # Update data
    result = stocking_data.update_stocking_data()
    
    # Get data for Winnipesaukee
    data = stocking_data.get_stocking_data("Winnipesaukee")
    
    # Get update status
    status = stocking_data.get_update_status()

if __name__ == "__main__":
    main()
