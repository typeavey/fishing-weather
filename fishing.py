import os
import json
import datetime
import logging
import requests
from typing import Union, List, Dict, Tuple


logger = logging.getLogger("fishing_forecast")


def configure_logging(level_str: Union[str, None] = None) -> None:
    level_name = (level_str or os.getenv("LOG_LEVEL") or "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger.debug("Logging configured: level=%s", logging.getLevelName(level))


def ensure_working_directory() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    logger.debug("Set working directory to %s", script_dir)


def load_config(config_path: str = "config.json") -> Tuple[str, str]:
    try:
        with open(config_path) as config_file:
            config = json.load(config_file)
    except FileNotFoundError as e:
        logger.error("Config file not found: %s", config_path)
        raise
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in config file: %s", config_path)
        raise
    api_key = config.get("api_key")
    output_dir = config.get("output_dir", os.getcwd())
    if not api_key:
        logger.error("'api_key' must be set in config.json")
        raise RuntimeError("Error: 'api_key' must be set in config.json.")
    logger.info("Loaded configuration. Output directory: %s", output_dir)
    return api_key, output_dir


def load_settings(settings_path: str = "settings.json") -> Tuple[Dict, Dict]:
    try:
        with open(settings_path) as settings_file:
            settings = json.load(settings_file)
    except FileNotFoundError:
        logger.error("Settings file not found: %s", settings_path)
        raise
    except json.JSONDecodeError:
        logger.error("Invalid JSON in settings file: %s", settings_path)
        raise
    locations = settings.get("locations", {})
    thresholds = settings.get("thresholds", {})
    if not locations:
        logger.error("'locations' must be defined in settings.json")
        raise RuntimeError("Error: 'locations' must be defined in settings.json.")
    logger.info("Loaded settings: %d location(s)", len(locations))
    return locations, thresholds


def extract_thresholds(thresholds: dict) -> dict:
    wind_speed_thresholds = thresholds.get("wind_speed", {})
    gust_thresholds = thresholds.get("wind_gust", {})
    temp_thresholds = thresholds.get("temp", {})

    th = {
        "wind_great": float(wind_speed_thresholds.get("great", 5)),
        "wind_good_min": float(wind_speed_thresholds.get("good_min", 6)),
        "wind_good_max": float(wind_speed_thresholds.get("good_max", 8)),
        "wind_bad_min": float(wind_speed_thresholds.get("bad_min", 9)),
        "wind_bad_max": float(wind_speed_thresholds.get("bad_max", 10)),
        "gust_gusty": float(gust_thresholds.get("gusty", 15)),
        "temp_cold": float(temp_thresholds.get("cold_max", 50)),
        "temp_hot": float(temp_thresholds.get("hot_min", 85)),
        "pressure_threshold": float(thresholds.get("pressure", 29.92)),
    }
    logger.debug("Thresholds: %s", th)
    return th


def fetch_forecast(lat: str, lon: str, api_key: str, *, timeout: int = 10) -> List[Dict]:
    onecall_url = (
        f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}"
        f"&exclude=current,minutely,hourly,alerts&units=imperial&appid={api_key}"
    )
    try:
        logger.info("Requesting forecast: lat=%s lon=%s", lat, lon)
        response = requests.get(onecall_url, timeout=timeout)
        response.raise_for_status()
        forecast_data = response.json()
    except requests.exceptions.RequestException as e:
        logger.warning("Failed to fetch forecast for lat=%s lon=%s: %s", lat, lon, e)
        return []
    except Exception as e:
        logger.warning("Failed to parse forecast response for lat=%s lon=%s: %s", lat, lon, e)
        return []
    daily_list = forecast_data.get("daily", [])[:8]
    if not daily_list:
        logger.warning("Empty or missing 'daily' forecast for lat=%s lon=%s", lat, lon)
    return daily_list


def determine_fishing_labels(
    wind_speed: Union[float, None],
    wind_gust: Union[float, None],
    temp_day: Union[float, None],
    pressure_in: Union[float, None],
    th: dict,
) -> Tuple[str, str]:
    # Base label from wind speed
    if wind_speed is None:
        fishing_base = ""
    elif wind_speed <= th["wind_great"]:
        fishing_base = "Great Fishing-Lite Wind"
    elif th["wind_good_min"] <= wind_speed <= th["wind_good_max"]:
        fishing_base = "Good Fishing-Moderate Wind"
    elif th["wind_bad_min"] <= wind_speed <= th["wind_bad_max"]:
        fishing_base = "Tough Fishing-High Wind"
    else:
        fishing_base = "Stay Home No Fishing"

    # Notes
    notes: List[str] = []
    if wind_gust and wind_gust > th["gust_gusty"]:
        notes.append("Gusty")
    if temp_day is not None:
        if temp_day < th["temp_cold"]:
            notes.append("Cold")
        elif temp_day > th["temp_hot"]:
            notes.append("Too Hot")
        else:
            notes.append("Comfortable Temp")
    if pressure_in is not None:
        if pressure_in < th["pressure_threshold"]:
            notes.append("Low Pressure")
        else:
            notes.append("High Pressure")

    fishing = f"{fishing_base} ({', '.join(notes)})" if fishing_base else ", ".join(notes)
    return fishing_base, fishing


def badge_html(base_label: str) -> str:
    color = "gray"
    if base_label.startswith("Great Fishing"):
        color = "green"
    elif base_label.startswith("Good Fishing"):
        color = "gold"
    elif base_label.startswith("Tough Fishing"):
        color = "orange"
    elif base_label.startswith("Stay Home No Fishing"):
        color = "red"
    return (
        "<span style='display:inline-block;width:12px;height:12px;"
        f"background-color:{color};border-radius:50%;margin-right:5px;'></span>"
    )


def build_rows_for_location(
    location_name: str,
    coords: dict,
    api_key: str,
    th: dict,
) -> List[Dict]:
    lat = coords.get("lat")
    lon = coords.get("lon")
    if not lat or not lon:
        logger.warning("Skipping location '%s' due to missing lat/lon", location_name)
        return []

    rows: List[Dict] = []
    days = fetch_forecast(lat, lon, api_key)
    logger.info("%s: received %d day(s) of forecast", location_name, len(days))
    for day_data in days:
        date_ts = datetime.datetime.fromtimestamp(day_data.get("dt"))
        date_str = date_ts.strftime("%A %m-%d-%Y")

        sunrise_ts = datetime.datetime.fromtimestamp(day_data.get("sunrise"))
        sunrise_str = sunrise_ts.strftime("%H:%M")

        summary = (
            day_data.get("summary")
            if day_data.get("summary")
            else day_data.get("weather", [{}])[0].get("description", "")
        )

        temp_day = day_data.get("temp", {}).get("day")

        pressure_hpa = day_data.get("pressure")
        pressure_in = round(pressure_hpa * 0.02953, 2) if pressure_hpa is not None else None

        wind_speed = day_data.get("wind_speed")
        wind_gust = day_data.get("wind_gust", 0)

        fishing_base, fishing = determine_fishing_labels(
            wind_speed, wind_gust, temp_day, pressure_in, th
        )

        rows.append(
            {
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
                "fishing_base": fishing_base,
            }
        )
    return rows


def group_rows_by_date(all_rows: List[Dict]) -> Dict[str, List[Dict]]:
    grouped: Dict[str, List[Dict]] = {}
    for row in all_rows:
        grouped.setdefault(row["date_str"], []).append(row)
    return grouped


def build_html(all_rows: List[Dict], th: dict) -> str:
    # Sort by datetime first
    all_rows.sort(key=lambda x: x["date_ts"])  # in-place
    grouped = group_rows_by_date(all_rows)
    logger.info("Building HTML for %d date(s)", len(grouped))

    # Legend
    legend_html = (
        f"<div style='margin-bottom:10px;'>"
        f"<strong>Legend:</strong> "
        f"<span style='color:green;'>● Great Fishing (≤ {th['wind_great']} mph wind)</span>, "
        f"<span style='color:gold;'>● Good Fishing ({th['wind_good_min']}-{th['wind_good_max']} mph wind)</span>, "
        f"<span style='color:orange;'>● Tough Fishing ({th['wind_bad_min']}-{th['wind_bad_max']} mph wind)</span>, "
        f"<span style='color:red;'>● No Fishing (&gt; {th['wind_bad_max']} mph wind)</span>"
        f"<br>Wind Gust Threshold: &gt; {th['gust_gusty']} mph is Gusty. "
        f"Pressure Standard: {th['pressure_threshold']} inHg (Low &lt; {th['pressure_threshold']}, High &gt;= {th['pressure_threshold']}). "
        f"Low pressure often indicates approaching storms and can stir fish activity, "
        f"while high pressure can calm conditions but may reduce fish feeding."
        f"</div>"
    )

    table_blocks: List[str] = [legend_html]

    # Timestamp of last successful run
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    table_blocks.append(
        f"<div style='font-size:0.9em; color:#555; margin-bottom:20px;'>Last updated: {timestamp}</div>"
    )

    for date_str, rows in grouped.items():
        table_blocks.append(f"<h2>{date_str}</h2>")
        block = [
            "<table>",
            "<thead><tr>",
            "<th>Location</th><th>Sunrise</th><th>Summary</th>",
            "<th>Temp (°F)</th><th>Pressure (inHg)</th>",
            "<th>Wind Speed (mph)</th><th>Wind Gust (mph)</th><th>Fishing</th>",
            "</tr></thead>",
            "<tbody>",
        ]
        for row in rows:
            badge = badge_html(row["fishing_base"])
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

    html_content = (
        """<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Fishing Forecast</title>
  <style>
    table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
    th, td { border: 1px solid #ccc; padding: 8px; text-align: left; vertical-align: top; word-wrap: break-word; white-space: normal; }
    th { background-color: #f2f2f2; }
    h2 { margin-top: 30px; }
  </style>
  </head>
  <body>
    <h1>8-Day Fishing Forecast</h1>
    """
        + "".join(table_blocks)
        + """
  </body>
</html>"""
    )
    return html_content


def write_html_file(html_content: str, output_dir: str) -> str:
    output_path = os.path.join(output_dir, "index.html")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    logger.info("Forecast HTML written to %s", output_path)
    return output_path


def main() -> None:
    configure_logging()
    ensure_working_directory()

    logger.info("Starting fishing forecast generation")
    api_key, output_dir = load_config()
    locations, thresholds_raw = load_settings()
    th = extract_thresholds(thresholds_raw)

    all_rows: List[Dict] = []
    for location_name, coords in locations.items():
        all_rows.extend(build_rows_for_location(location_name, coords, api_key, th))

    html_content = build_html(all_rows, th)
    write_html_file(html_content, output_dir)
    logger.info("Completed fishing forecast generation")


if __name__ == "__main__":
    main()