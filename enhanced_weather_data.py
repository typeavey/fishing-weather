#!/usr/bin/env python3
"""
Enhanced Weather Data Access
Demonstrates how to access all available weather data from OpenWeatherMap API
"""

import requests
import datetime
from typing import Dict, List, Any

def fetch_complete_weather_data(lat: str, lon: str, api_key: str) -> Dict[str, Any]:
    """
    Fetch complete weather data including all available fields
    """
    onecall_url = (
        f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}"
        f"&exclude=current,minutely,hourly,alerts&units=imperial&appid={api_key}"
    )
    
    try:
        response = requests.get(onecall_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return {}

def extract_all_weather_fields(daily_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract all available weather fields from daily data
    """
    return {
        # Basic info
        "date": datetime.datetime.fromtimestamp(daily_data.get("dt")),
        "sunrise": datetime.datetime.fromtimestamp(daily_data.get("sunrise")),
        "sunset": datetime.datetime.fromtimestamp(daily_data.get("sunset")),
        "summary": daily_data.get("summary"),
        
        # Temperature data (6 fields)
        "temp_day": daily_data.get("temp", {}).get("day"),
        "temp_min": daily_data.get("temp", {}).get("min"),
        "temp_max": daily_data.get("temp", {}).get("max"),
        "temp_night": daily_data.get("temp", {}).get("night"),
        "temp_eve": daily_data.get("temp", {}).get("eve"),
        "temp_morn": daily_data.get("temp", {}).get("morn"),
        
        # Feels like temperature (4 fields)
        "feels_like_day": daily_data.get("feels_like", {}).get("day"),
        "feels_like_night": daily_data.get("feels_like", {}).get("night"),
        "feels_like_eve": daily_data.get("feels_like", {}).get("eve"),
        "feels_like_morn": daily_data.get("feels_like", {}).get("morn"),
        
        # Atmospheric data (3 fields)
        "pressure": daily_data.get("pressure"),
        "humidity": daily_data.get("humidity"),
        "dew_point": daily_data.get("dew_point"),
        
        # Wind data (3 fields)
        "wind_speed": daily_data.get("wind_speed"),
        "wind_deg": daily_data.get("wind_deg"),
        "wind_gust": daily_data.get("wind_gust"),
        
        # Astronomical data (4 fields)
        "moonrise": datetime.datetime.fromtimestamp(daily_data.get("moonrise")),
        "moonset": datetime.datetime.fromtimestamp(daily_data.get("moonset")),
        "moon_phase": daily_data.get("moon_phase"),
        
        # Cloud and visibility (2 fields)
        "clouds": daily_data.get("clouds"),
        "uvi": daily_data.get("uvi"),
        
        # Precipitation data (3 fields)
        "pop": daily_data.get("pop"),  # Probability of precipitation
        "rain": daily_data.get("rain"),
        "snow": daily_data.get("snow"),
        
        # Weather description
        "weather_id": daily_data.get("weather", [{}])[0].get("id"),
        "weather_main": daily_data.get("weather", [{}])[0].get("main"),
        "weather_description": daily_data.get("weather", [{}])[0].get("description"),
        "weather_icon": daily_data.get("weather", [{}])[0].get("icon"),
    }

def analyze_fishing_conditions(weather_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced fishing condition analysis using all available data
    """
    conditions = {}
    
    # Temperature analysis
    temp_day = weather_data.get("temp_day")
    temp_min = weather_data.get("temp_min")
    temp_max = weather_data.get("temp_max")
    
    if temp_day:
        if temp_day < 40:
            conditions["temperature_rating"] = "Cold - Fish may be less active"
        elif temp_day > 85:
            conditions["temperature_rating"] = "Hot - Fish may seek deeper water"
        else:
            conditions["temperature_rating"] = "Ideal temperature for fishing"
    
    # Wind analysis
    wind_speed = weather_data.get("wind_speed")
    wind_deg = weather_data.get("wind_deg")
    wind_gust = weather_data.get("wind_gust")
    
    if wind_speed:
        if wind_speed <= 5:
            conditions["wind_rating"] = "Light winds - Excellent for fishing"
        elif wind_speed <= 10:
            conditions["wind_rating"] = "Moderate winds - Good for fishing"
        elif wind_speed <= 15:
            conditions["wind_rating"] = "Strong winds - Challenging fishing"
        else:
            conditions["wind_rating"] = "High winds - Poor fishing conditions"
    
    # Pressure analysis
    pressure = weather_data.get("pressure")
    if pressure:
        if pressure < 1013:
            conditions["pressure_rating"] = "Low pressure - Fish may be more active"
        else:
            conditions["pressure_rating"] = "High pressure - Stable conditions"
    
    # Humidity and moisture
    humidity = weather_data.get("humidity")
    dew_point = weather_data.get("dew_point")
    pop = weather_data.get("pop")
    
    if humidity and dew_point:
        conditions["moisture_analysis"] = f"Humidity: {humidity}%, Dew Point: {dew_point}°F"
    
    if pop:
        conditions["precipitation_chance"] = f"{pop * 100:.0f}% chance of precipitation"
    
    # UV Index
    uvi = weather_data.get("uvi")
    if uvi:
        if uvi <= 2:
            conditions["uv_rating"] = "Low UV - Good for all-day fishing"
        elif uvi <= 5:
            conditions["uv_rating"] = "Moderate UV - Morning/evening fishing recommended"
        else:
            conditions["uv_rating"] = "High UV - Early morning/late evening fishing best"
    
    return conditions

def print_enhanced_weather_report(weather_data: Dict[str, Any]):
    """
    Print a comprehensive weather report using all available data
    """
    print(f"\n🌤️ Enhanced Weather Report for {weather_data['date'].strftime('%A, %B %d, %Y')}")
    print("=" * 60)
    
    # Temperature section
    print(f"\n🌡️ Temperature Data:")
    print(f"  Day: {weather_data['temp_day']}°F (Feels like: {weather_data['feels_like_day']}°F)")
    print(f"  Min: {weather_data['temp_min']}°F | Max: {weather_data['temp_max']}°F")
    print(f"  Night: {weather_data['temp_night']}°F | Evening: {weather_data['temp_eve']}°F | Morning: {weather_data['temp_morn']}°F")
    
    # Wind section
    print(f"\n💨 Wind Data:")
    print(f"  Speed: {weather_data['wind_speed']} mph")
    print(f"  Direction: {weather_data['wind_deg']}° ({get_wind_direction(weather_data['wind_deg'])})")
    print(f"  Gusts: {weather_data['wind_gust']} mph")
    
    # Atmospheric section
    print(f"\n🌬️ Atmospheric Data:")
    print(f"  Pressure: {weather_data['pressure']} hPa ({weather_data['pressure'] * 0.02953:.2f} inHg)")
    print(f"  Humidity: {weather_data['humidity']}%")
    print(f"  Dew Point: {weather_data['dew_point']}°F")
    
    # Astronomical section
    print(f"\n🌙 Astronomical Data:")
    print(f"  Sunrise: {weather_data['sunrise'].strftime('%H:%M')}")
    print(f"  Sunset: {weather_data['sunset'].strftime('%H:%M')}")
    print(f"  Moonrise: {weather_data['moonrise'].strftime('%H:%M')}")
    print(f"  Moonset: {weather_data['moonset'].strftime('%H:%M')}")
    print(f"  Moon Phase: {get_moon_phase_name(weather_data['moon_phase'])}")
    
    # Cloud and UV section
    print(f"\n☁️ Cloud & UV Data:")
    print(f"  Cloud Cover: {weather_data['clouds']}%")
    print(f"  UV Index: {weather_data['uvi']} ({get_uv_rating(weather_data['uvi'])})")
    
    # Precipitation section
    print(f"\n🌧️ Precipitation Data:")
    print(f"  Probability: {weather_data['pop'] * 100:.0f}%")
    if weather_data.get('rain'):
        print(f"  Rain: {weather_data['rain']} mm")
    if weather_data.get('snow'):
        print(f"  Snow: {weather_data['snow']} mm")
    
    # Fishing analysis
    fishing_conditions = analyze_fishing_conditions(weather_data)
    print(f"\n🎣 Fishing Analysis:")
    for condition, rating in fishing_conditions.items():
        print(f"  {condition.replace('_', ' ').title()}: {rating}")

def get_wind_direction(degrees: int) -> str:
    """Convert wind degrees to cardinal direction"""
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = round(degrees / 22.5) % 16
    return directions[index]

def get_moon_phase_name(phase: float) -> str:
    """Convert moon phase number to name"""
    phases = {
        0: "New Moon",
        0.25: "First Quarter",
        0.5: "Full Moon",
        0.75: "Last Quarter"
    }
    return phases.get(phase, f"Phase {phase:.2f}")

def get_uv_rating(uvi: float) -> str:
    """Convert UV index to rating"""
    if uvi <= 2:
        return "Low"
    elif uvi <= 5:
        return "Moderate"
    elif uvi <= 7:
        return "High"
    elif uvi <= 10:
        return "Very High"
    else:
        return "Extreme"

if __name__ == "__main__":
    # Example usage
    print("🎣 Enhanced Weather Data Access Demo")
    print("This shows all available weather data from OpenWeatherMap API")
    
    # You would need to replace with actual API key and coordinates
    # api_key = "your_api_key_here"
    # lat, lon = "43.6406", "-72.144"
    
    print("\nTo use this enhanced data access:")
    print("1. Replace the API key and coordinates")
    print("2. Call fetch_complete_weather_data()")
    print("3. Use extract_all_weather_fields() to get all data")
    print("4. Use analyze_fishing_conditions() for enhanced fishing analysis")
