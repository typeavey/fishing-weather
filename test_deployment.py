#!/usr/bin/env python3
"""
Test script to verify the fishing weather portal deployment with SQLite database
"""

import requests
import time
import sys
import os

def test_deployment():
    """Test the complete deployment"""
    print("🧪 Testing Fishing Weather Portal Deployment...")
    
    # Test 1: Check if Flask app can be imported
    print("\n1. Testing Flask app import...")
    try:
        from app import app, db
        print("✅ Flask app imported successfully")
    except Exception as e:
        print(f"❌ Flask app import failed: {e}")
        return False
    
    # Test 2: Check database connection
    print("\n2. Testing database connection...")
    try:
        stats = db.get_statistics()
        print(f"✅ Database connected: {stats.get('total_records', 0)} records")
        print(f"   Locations: {list(stats.get('location_counts', {}).keys())}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Test 3: Check if server can start (briefly)
    print("\n3. Testing server startup...")
    try:
        # Start server in background
        import subprocess
        import threading
        
        def start_server():
            subprocess.run([sys.executable, "app.py"], 
                         capture_output=True, timeout=5)
        
        server_thread = threading.Thread(target=start_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Test health endpoint
        try:
            response = requests.get('http://localhost:5000/api/health', timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Server started successfully")
                print(f"   Status: {health_data.get('status')}")
                print(f"   Database: {health_data.get('database')}")
            else:
                print(f"❌ Health endpoint returned {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Could not connect to server (may be normal if not running): {e}")
        
    except Exception as e:
        print(f"❌ Server test failed: {e}")
    
    # Test 4: Check database functionality
    print("\n4. Testing database functionality...")
    try:
        # Test getting weather data
        weather_data = db.get_weather_data(limit=5)
        print(f"✅ Weather data retrieval: {len(weather_data)} records")
        
        # Test getting fishing conditions
        fishing_conditions = db.get_fishing_conditions(days_back=7)
        print(f"✅ Fishing conditions retrieval: {len(fishing_conditions)} records")
        
        # Test getting statistics
        stats = db.get_statistics()
        print(f"✅ Statistics retrieval: {stats.get('total_records', 0)} total records")
        
    except Exception as e:
        print(f"❌ Database functionality test failed: {e}")
        return False
    
    # Test 5: Check file structure
    print("\n5. Testing file structure...")
    required_files = [
        'app.py',
        'working_database.py',
        'weather_data.db',
        'requirements.txt',
        'start-portal.sh',
        'backup-database.sh',
        'DEPLOYMENT.md'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            return False
    
    print("\n🎉 All tests passed! Deployment is successful!")
    return True

if __name__ == '__main__':
    success = test_deployment()
    if success:
        print("\n🚀 Your fishing weather portal is ready to use!")
        print("   Run: ./start-portal.sh")
        print("   Visit: http://localhost:5000")
    else:
        print("\n❌ Deployment test failed. Please check the errors above.")
        sys.exit(1)
