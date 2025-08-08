#!/usr/bin/env python3
"""
Test script for enhanced fishing analysis
"""

import json
from enhanced_fishing_analysis import EnhancedFishingAnalysis

def test_enhanced_analysis():
    """Test the enhanced fishing analysis with sample data"""
    print("🧪 Testing Enhanced Fishing Analysis...")
    
    # Sample weather data
    sample_weather_data = {
        "dt": 1748880000,
        "sunrise": 1748855375,
        "sunset": 1748910239,
        "moonrise": 1748880000,
        "moonset": 1748841000,
        "moon_phase": 0.25,
        "summary": "There will be clear sky until morning, then partly cloudy",
        "temp": {
            "day": 63.81,
            "min": 37.65,
            "max": 67.15,
            "night": 53.53,
            "eve": 60.71,
            "morn": 45.23
        },
        "feels_like": {
            "day": 62.24,
            "night": 52.16,
            "eve": 59.4,
            "morn": 45.23
        },
        "pressure": 1012,
        "humidity": 50,
        "dew_point": 38.43,
        "wind_speed": 12.55,
        "wind_deg": 276,
        "wind_gust": 17.05,
        "weather": [
            {
                "id": 802,
                "main": "Clouds",
                "description": "scattered clouds",
                "icon": "03d"
            }
        ],
        "clouds": 44,
        "pop": 0.82,
        "uvi": 6.36
    }
    
    # Initialize enhanced analysis
    enhanced_analysis = EnhancedFishingAnalysis()
    
    # Analyze fishing conditions
    analysis = enhanced_analysis.analyze_fishing_conditions(sample_weather_data)
    
    print(f"✅ Analysis completed successfully!")
    print(f"📊 Overall Score: {analysis['overall_score']}/100")
    print(f"🎣 Fishing Rating: {analysis['fishing_rating']}")
    print(f"📝 Detailed Summary: {analysis['detailed_summary']}")
    
    # Print detailed analysis
    print("\n🔍 Detailed Analysis:")
    print(f"  Wind: {analysis['wind_analysis']['speed_description']}")
    print(f"  Temperature: {analysis['temperature_analysis']['description']}")
    print(f"  Weather: {analysis['weather_analysis']['description_text']}")
    print(f"  Pressure: {analysis['pressure_analysis']['description']}")
    print(f"  Moon: {analysis['moon_analysis']['description']}")
    
    # Print recommendations
    if analysis['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in analysis['recommendations']:
            print(f"  • {rec}")
    
    return analysis

def test_different_conditions():
    """Test different weather conditions"""
    print("\n🧪 Testing Different Weather Conditions...")
    
    # Test scenarios
    scenarios = [
        {
            "name": "Perfect Fishing Day",
            "data": {
                "wind_speed": 3.0,
                "wind_gust": 5.0,
                "wind_deg": 180,
                "temp": {"day": 65.0},
                "pressure": 1000,  # Low pressure
                "moon_phase": 1.0,  # Full moon
                "weather": [{"main": "Clouds", "description": "overcast clouds"}],
                "clouds": 90
            }
        },
        {
            "name": "Challenging Day",
            "data": {
                "wind_speed": 18.0,
                "wind_gust": 25.0,
                "wind_deg": 270,
                "temp": {"day": 90.0},
                "pressure": 1020,  # High pressure
                "moon_phase": 0.0,  # New moon
                "weather": [{"main": "Clear", "description": "clear sky"}],
                "clouds": 10
            }
        },
        {
            "name": "Rainy Day",
            "data": {
                "wind_speed": 8.0,
                "wind_gust": 12.0,
                "wind_deg": 45,
                "temp": {"day": 55.0},
                "pressure": 1010,
                "moon_phase": 0.5,
                "weather": [{"main": "Rain", "description": "light rain"}],
                "clouds": 100
            }
        }
    ]
    
    enhanced_analysis = EnhancedFishingAnalysis()
    
    for scenario in scenarios:
        print(f"\n📅 {scenario['name']}:")
        analysis = enhanced_analysis.analyze_fishing_conditions(scenario['data'])
        print(f"  Score: {analysis['overall_score']}/100")
        print(f"  Rating: {analysis['fishing_rating']}")
        print(f"  Summary: {analysis['detailed_summary']}")

if __name__ == "__main__":
    # Test basic functionality
    test_enhanced_analysis()
    
    # Test different conditions
    test_different_conditions()
    
    print("\n🎉 Enhanced fishing analysis test completed!")
