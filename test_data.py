#!/usr/bin/env python3
"""
Test script for weather data structure
"""

from app import get_cached_weather_data

def test_data_structure():
    """Test the weather data structure"""
    print("🔍 Testing weather data structure...")
    
    data = get_cached_weather_data()
    
    if not data:
        print("❌ No weather data generated")
        return False
    
    print(f"✅ Total records: {len(data)}")
    
    # Check locations
    locations = set(item['location'] for item in data)
    print(f"✅ Locations found: {locations}")
    
    # Check date range
    dates = [item['date_str'] for item in data]
    print(f"✅ Date range: {min(dates)} to {max(dates)}")
    
    # Check sample record structure
    sample = data[0]
    expected_keys = ['date_ts', 'location', 'date_str', 'sunrise', 'summary', 'temp', 'pressure', 'wind_speed', 'wind_gust', 'fishing', 'fishing_base']
    
    missing_keys = [key for key in expected_keys if key not in sample]
    if missing_keys:
        print(f"❌ Missing keys in sample record: {missing_keys}")
        return False
    
    print(f"✅ Sample record structure: {list(sample.keys())}")
    print(f"✅ Sample record: {sample['location']} - {sample['date_str']} - {sample['fishing']}")
    
    # Check fishing conditions
    conditions = set(item['fishing_base'] for item in data)
    print(f"✅ Fishing conditions: {conditions}")
    
    return True

if __name__ == '__main__':
    success = test_data_structure()
    if success:
        print("\n🎉 Data structure test passed!")
    else:
        print("\n❌ Data structure test failed!")
        exit(1)
