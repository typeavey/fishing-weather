import requests
import datetime
import json

# Read the API key from config.json
with open("config.json") as config_file:
    config = json.load(config_file)
    api_key = config.get("api_key")

# Read settings (locations and thresholds) from settings.json
with open("settings.json") as settings_file:
    settings = json.load(settings_file)
    locations = settings.get("locations", {})
    thresholds = settings.get("thresholds", {})

if not api_key:
    print("Error: 'api_key' must be set in config.json.")
    exit(1)
if not locations:
    print("Error: 'locations' must be defined in settings.json.")
    exit(1)

# Extract threshold values
wind_speed_thresholds = thresholds.get("wind_speed", {})
wind_great = float(wind_speed_thresholds.get("great", 5))
wind_good_min = float(wind_speed_thresholds.get("good_min", 6))
wind_good_max = float(wind_speed_thresholds.get("good_max", 8))
wind_bad_min = float(wind_speed_thresholds.get("bad_min", 9))
wind_bad_max = float(wind_speed_thresholds.get("bad_max", 10))

gust_thresholds = thresholds.get("wind_gust", {})
gust_gusty = float(gust_thresholds.get("gusty", 15))

temp_thresholds = thresholds.get("temp", {})
temp_cold = float(temp_thresholds.get("cold_max", 50))
temp_hot = float(temp_thresholds.get("hot_min", 85))

pressure_threshold = float(thresholds.get("pressure", 29.92))

# Container for all rows
all_rows = []

for location_name, coords in locations.items():
    lat = coords.get("lat")
    lon = coords.get("lon")
    if not lat or not lon:
        continue

    # Fetch 8-day forecast for this location
    onecall_url = (
        f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}"
        f"&exclude=current,minutely,hourly,alerts&units=imperial&appid={api_key}"
    )
    try:
        response = requests.get(onecall_url)
        response.raise_for_status()
        forecast_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {location_name}: {e}")
        continue

    # Extract daily forecasts (up to 8 days)
    daily_list = forecast_data.get('daily', [])[:8]
    for day_data in daily_list:
        # Parse date
        date_ts = datetime.datetime.fromtimestamp(day_data.get('dt'))
        date_str = date_ts.strftime('%A %m-%d-%Y')

        # Sunrise
        sunrise_ts = datetime.datetime.fromtimestamp(day_data.get('sunrise'))
        sunrise_str = sunrise_ts.strftime('%H:%M')

        # Summary
        summary = day_data.get('summary') if day_data.get('summary') else day_data.get('weather', [{}])[0].get('description', '')
        summary = summary[:38] + ".." if len(summary) > 40 else summary

        # Temperature
        temp_day = day_data.get('temp', {}).get('day')

        # Pressure
        pressure_hpa = day_data.get('pressure')
        pressure_in = round(pressure_hpa * 0.02953, 2) if pressure_hpa is not None else None

        # Wind speed and gust
        wind_speed = day_data.get('wind_speed')
        wind_gust = day_data.get('wind_gust', 0)

        # Base fishing condition
        if wind_speed is None:
            fishing_base = ""
        elif wind_speed <= wind_great:
            fishing_base = "Lite Wind"
        elif wind_good_min <= wind_speed <= wind_good_max:
            fishing_base = "Moderate Wind"
        elif wind_bad_min <= wind_speed <= wind_bad_max:
            fishing_base = "High Wind"
        else:
            fishing_base = "Absolutely no fishing"

        # Additional notes: gust, temp, pressure
        notes = []
        if wind_gust and wind_gust > gust_gusty:
            notes.append("Gusty")
        if temp_day is not None:
            if temp_day < temp_cold:
                notes.append("Cold")
            elif temp_day > temp_hot:
                notes.append("Too Hot")
            else:
                notes.append("Comfortable Temp")
        if pressure_in is not None:
            if pressure_in < pressure_threshold:
                notes.append("Low Pressure")
            else:
                notes.append("High Pressure")

        fishing = f"{fishing_base} ({', '.join(notes)})" if fishing_base else ", ".join(notes)

        # Append row dict
        all_rows.append({
            "date_ts": date_ts,
            "location": location_name,
            "date_str": date_str,
            "sunrise": sunrise_str,
            "summary": summary,
            "temp": temp_day,
            "pressure": pressure_in,
            "wind_speed": wind_speed,
            "wind_gust": wind_gust,
            "fishing": fishing
        })

# Sort all rows by date
all_rows.sort(key=lambda x: x["date_ts"])

# Print combined table header
header = ["Location", "Date", "Sunrise", "Summary", "Temp (°F)", "Pressure (inHg)", "Wind Speed (mph)", "Wind Gust (mph)", "Fishing"]
print(f"{header[0]:<15} {header[1]:<22} {header[2]:<8} {header[3]:<40} {header[4]:<12} {header[5]:<16} {header[6]:<18} {header[7]:<18} {header[8]:<30}")
print("-" * 225)

# Print each row in sorted order
for row in all_rows:
    print(f"{row['location']:<15} {row['date_str']:<22} {row['sunrise']:<8} {row['summary']:<40} {str(row['temp']):<12} {str(row['pressure']):<16} {str(row['wind_speed']):<18} {str(row['wind_gust']):<18} {row['fishing']:<30}")
