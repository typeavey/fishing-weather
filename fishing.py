import requests
import datetime
import json

# Read the API key from config.json
with open("config.json") as config_file:
    config = json.load(config_file)
    api_key = config["api_key"]

lon = "-72.144"
lat = "43.6406"
url = f"https://api.openweathermap.org/data/2.5/forecast/?lat={lat}&lon={lon}&cnt=7&appid={api_key}&units=imperial"

response = requests.get(url)
weather_data = response.json()

# Initialize a dictionary to store the daily wind gust data
daily_wind_gust = {}

# Iterate through the list of weather data
for forecast in weather_data['list']:
    forecast_time = datetime.datetime.fromtimestamp(forecast['dt'])
    day_of_week = forecast_time.strftime('%A')

    temp = forecast['main']['temp']
    wind_speed = forecast['wind']['speed']
    wind_gust = forecast['wind']['gust']

    # Group and sum the wind gusts by date
    date_str = forecast_time.strftime('%Y-%m-%d')
    daily_wind_gust.setdefault(date_str, []).append(wind_gust)

    # Check if the wind gust is above 6
    if wind_gust > 6:
        print(f"{day_of_week}: Temperature = {temp}°F, Wind Speed = {wind_speed} m/s, Wind Gust = {wind_gust} m/s - Good Fishing Day")
    else:
        print(f"{day_of_week}: Temperature = {temp}°F, Wind Speed = {wind_speed} m/s, Wind Gust = {wind_gust} m/s")

# Optional: Calculate the average wind gust for each day
for date, gusts in daily_wind_gust.items():
    average_wind_gust = sum(gusts) / len(gusts)
    print(f"{date} - Average Wind Gust: {average_wind_gust:.2f} m/s")
