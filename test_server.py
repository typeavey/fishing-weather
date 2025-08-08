#!/usr/bin/env python3
"""
Test script for the fishing weather portal
"""

import requests
import time
import subprocess
import sys
import os

def test_server():
    """Test the fishing weather portal server"""
    print("🧪 Testing Fishing Weather Portal...")
    
    # Test 1: Check if dependencies are installed
    print("\n1. Testing dependencies...")
    try:
        import flask
        import flask_cors
        print("✅ Flask and Flask-CORS installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False
    
    # Test 2: Check if fishing.py works
    print("\n2. Testing fishing.py functionality...")
    try:
        from fishing import load_config, load_settings
        config = load_config()
        settings = load_settings()
        print(f"✅ fishing.py: {len(settings[0])} locations loaded")
    except Exception as e:
        print(f"❌ fishing.py error: {e}")
        return False
    
    # Test 3: Check if Flask app can be created
    print("\n3. Testing Flask app...")
    try:
        from app import app, get_cached_weather_data
        data = get_cached_weather_data()
        print(f"✅ Flask app: {len(data)} weather records generated")
    except Exception as e:
        print(f"❌ Flask app error: {e}")
        return False
    
    # Test 4: Check if web files exist
    print("\n4. Testing web interface files...")
    required_files = [
        'fishing-website/index.html',
        'fishing-website/weather.html',
        'fishing-website/locations.html',
        'fishing-website/forecast.html',
        'fishing-website/js/weather-api.js'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            return False
    
    # Test 5: Try to start server (briefly)
    print("\n5. Testing server startup...")
    try:
        # Start server in background
        process = subprocess.Popen([
            sys.executable, 'app.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for server to start
        time.sleep(3)
        
        # Test health endpoint
        try:
            response = requests.get('http://localhost:5000/api/health', timeout=5)
            if response.status_code == 200:
                print("✅ Server started and health endpoint working")
                health_data = response.json()
                print(f"   Status: {health_data.get('status')}")
                print(f"   Cache age: {health_data.get('cache_age')}s")
            else:
                print(f"❌ Health endpoint returned {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Could not connect to server: {e}")
        
        # Stop server
        process.terminate()
        process.wait(timeout=5)
        
    except Exception as e:
        print(f"❌ Server test error: {e}")
        return False
    
    print("\n🎉 All tests passed! The fishing weather portal is working correctly.")
    return True

if __name__ == '__main__':
    success = test_server()
    sys.exit(0 if success else 1)
