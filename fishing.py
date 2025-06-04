import requests
import datetime
import json
import os

# Ensure script's working directory is its own directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Read config.json for API key and output directory
with open("config.json") as config_file:
    config = json.load(config_file)
    api_key = config.get("api_key")
    output_dir = config.get("output_dir", os.getcwd())  # fallback to current dir

# Read settings (locations and thresholds) from settings.json
with open("settings.json") as settings_file:
    settings = json.load(settings_file)
    locations = settings.get("locations", {})
    thresholds = settings.get("thresholds", {})

if not api_key:
    raise RuntimeError("Error: 'api_key' must be set in config.json.")
if not locations:
    raise RuntimeError("Error: 'locations' must be defined in settings.json.")

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
    except requests.exceptions.RequestException:
        continue

    # Extract daily forecasts (up to 8 days)
    daily_list = forecast_data.get('daily', [])[:8]
    for day_data in daily_list:
        date_ts = datetime.datetime.fromtimestamp(day_data.get('dt'))
        date_str = date_ts.strftime('%A %m-%d-%Y')

        sunrise_ts = datetime.datetime.fromtimestamp(day_data.get('sunrise'))
        sunrise_str = sunrise_ts.strftime('%H:%M')

        summary = day_data.get('summary') if day_data.get('summary') else day_data.get('weather', [{}])[0].get('description', '')

        temp_day = day_data.get('temp', {}).get('day')

        pressure_hpa = day_data.get('pressure')
        pressure_in = round(pressure_hpa * 0.02953, 2) if pressure_hpa is not None else None

        wind_speed = day_data.get('wind_speed')
        wind_gust = day_data.get('wind_gust', 0)

        # Determine fishing base label
        if wind_speed is None:
            fishing_base = ""
        elif wind_speed <= wind_great:
            fishing_base = "Great Fishing-Lite Wind"
        elif wind_good_min <= wind_speed <= wind_good_max:
            fishing_base = "Good Fishing-Moderate Wind"
        elif wind_bad_min <= wind_speed <= wind_bad_max:
            fishing_base = "Tough Fishing-High Wind"
        else:
            fishing_base = "Stay Home No Fishing"

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
            "fishing": fishing,
            "fishing_base": fishing_base
        })

# Sort rows by date
all_rows.sort(key=lambda x: x["date_ts"])

# Group rows by date_str
grouped = {}
for row in all_rows:
    grouped.setdefault(row["date_str"], []).append(row)

# Function to generate badge HTML based on fishing_base
def badge_html(base_label):
    color = "gray"
    if base_label.startswith("Great Fishing"):
        color = "green"
    elif base_label.startswith("Good Fishing"):
        color = "gold"
    elif base_label.startswith("Tough Fishing"):
        color = "orange"
    elif base_label.startswith("Stay Home No Fishing"):
        color = "red"
    return f"<span style='display:inline-block;width:12px;height:12px;background-color:{color};border-radius:50%;margin-right:5px;'></span>"

# Build HTML content
table_blocks = []
legend_html = (
    f"<div style='margin-bottom:10px;'>"
    f"<strong>Legend:</strong> "
    f"<span style='color:green;'>● Great Fishing (≤ {wind_great} mph wind)</span>, "
    f"<span style='color:gold;'>● Good Fishing ({wind_good_min}-{wind_good_max} mph wind)</span>, "
    f"<span style='color:orange;'>● Tough Fishing ({wind_bad_min}-{wind_bad_max} mph wind)</span>, "
    f"<span style='color:red;'>● No Fishing (&gt; {wind_bad_max} mph wind)</span>"
    f"<br>Wind Gust Threshold: &gt; {gust_gusty} mph is Gusty. "
    f"Pressure Standard: {pressure_threshold} inHg (Low &lt; {pressure_threshold}, High &gt;= {pressure_threshold}). "
    f"Low pressure often indicates approaching storms and can stir fish activity, "
    f"while high pressure can calm conditions but may reduce fish feeding."
    f"</div>"
)
table_blocks.append(legend_html)

for date_str, rows in grouped.items():
    table_blocks.append(f"<h2>{date_str}</h2>")
    block = [
        "<table>",
        "<thead><tr>",
        "<th>Location</th><th>Sunrise</th><th>Summary</th>",
        "<th>Temp (°F)</th><th>Pressure (inHg)</th>",
        "<th>Wind Speed (mph)</th><th>Wind Gust (mph)</th><th>Fishing</th>",
        "</tr></thead>",
        "<tbody>"
    ]
    for row in rows:
        badge = badge_html(row['fishing_base'])
        block.append(
            f"<tr>"
            f"<td>{row['location']}</td>"
            f"<td>{row['sunrise']}</td>"
            f"<td>{row['summary']}</td>"
            f"<td>{row['temp']}</td>"
            f"<td>{row['pressure']}</td>"
            f"<td>{row['wind_speed']}</td>"
            f"<td>{row['wind_gust']}</td>"
            f"<td>{badge}{row['fishing']}</td>"
            f"</tr>"
        )
    block.append("</tbody></table>")
    table_blocks.append("".join(block))

html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Fishing Forecast</title>
  <style>
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
    th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; vertical-align: top; word-wrap: break-word; white-space: normal; }}
    th {{ background-color: #f2f2f2; }}
    h2 {{ margin-top: 30px; }}
  </style>
</head>
<body>
  <h1>8-Day Fishing Forecast</h1>
  {"".join(table_blocks)}
</body>
</html>
"""

# Use output_dir from config.json
output_path = os.path.join(output_dir, "index.html")
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Write the HTML file
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Forecast HTML written to {output_path}")
