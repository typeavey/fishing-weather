# Fishing Forecast Automation

This repository contains a Python script that fetches 8-day weather forecasts for multiple lakes, evaluates “fishing conditions” based on configurable thresholds (wind, temperature, pressure), and generates a styled HTML page grouped by date with visual condition badges. Structured logging is included for observability.

---

## Contents

* **`fishing.py`**
  Main Python script that reads API credentials and settings, retrieves weather data from OpenWeatherMap’s One Call API (3.0), computes “fishing” status, and writes a styled `index.html` to your configured output directory.

* **`config.json`**
  Contains API and output configuration:

  ```json
  {
    "api_key": "YOUR_OPENWEATHERMAP_API_KEY",
    "output_dir": "/absolute/path/where/html/should/be/written"
  }
  ```

  * **`api_key`**: Your OpenWeatherMap API key (One Call 3.0 must be enabled on your account).
  * **`output_dir`**: Directory where the generated `index.html` will be written (the script will create it if needed).

* **`settings.json`**
  Defines the lakes/locations and all threshold values used to categorize fishing conditions:

  ```json
  {
    "locations": {
      "Winnipesaukee": { "lat": "43.6406", "lon": "-72.1440" },
      "Newfound":     { "lat": "43.7528", "lon": "-71.7999" },
      "Squam":        { "lat": "43.8280", "lon": "-71.5503" },
      "Champlain":    { "lat": "44.4896", "lon": "-73.3582" },
      "Mascoma":      { "lat": "43.6587", "lon": "-72.3200" }
    },
    "thresholds": {
      "wind_speed": {
        "great":    5,
        "good_min": 6,
        "good_max": 8,
        "bad_min":  9,
        "bad_max":  10
      },
      "wind_gust": {
        "gusty": 15
      },
      "temp": {
        "cold_max": 50,
        "hot_min":  85
      },
      "pressure": 29.92
    }
  }
  ```

  * **`locations`**: A dictionary of `{ "LocationName": { "lat": "...", "lon": "..." } }`. Add or remove any lake coordinates here.
  * **`thresholds.wind_speed`**:

    * `great`: ≤ X mph → “Lite Wind”
    * `good_min`–`good_max`: Y–Z mph → “Moderate Wind”
    * `bad_min`–`bad_max`: A–B mph → “High Wind”
    * `> bad_max`: → “Absolutely no fishing”
  * **`thresholds.wind_gust.gusty`**: any gust > X mph → append “Gusty”
  * **`thresholds.temp`**:

    * `< cold_max` °F → append “Cold”
    * `> hot_min` °F → append “Too Hot”
    * otherwise → append “Comfortable Temp”
  * **`thresholds.pressure`**: inHg threshold; `<` → append “Low Pressure”, otherwise → “High Pressure”

---

## Prerequisites

1. **Python 3.10+** (required for newer type hints used; tested on 3.10 and 3.11)
2. **PIP** (for installing dependencies)
3. **An OpenWeatherMap API key** (One Call API 3.0 enabled).

   * Sign up at [OpenWeatherMap](https://openweathermap.org/) and enable the One Call 3.0 subscription.

---

## Installation

1. **Create a virtual environment (recommended)**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate      # macOS/Linux
   # venv\Scripts\activate.bat   # Windows
   ```

2. **Install required packages**:

   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration

1. **Populate `config.json`**

   ```json
   {
     "api_key": "YOUR_OPENWEATHERMAP_API_KEY",
     "output_dir": "/absolute/path/to/output"
   }
   ```

   Replace `"YOUR_OPENWEATHERMAP_API_KEY"` with your actual key. `output_dir` is where `index.html` will be written.

2. **Customize `settings.json`**

   * Add or remove locations under `"locations"`.
   * Adjust threshold values under `"thresholds"`.
   * Ensure all numeric values (wind, gust, temp, pressure) match the units (mph for winds, °F for temp, inHg for pressure).

---

## Usage

Generate the HTML page at `output_dir/index.html`:

```bash
python fishing.py
```

Using the project venv explicitly:

```bash
fishing-weather/venv/bin/python fishing.py
```

What happens:

1. Loads your API key and target output directory from `config.json`.
2. Loads locations and thresholds from `settings.json`.
3. Calls the One Call 3.0 API for each lake’s latitude/longitude.
4. Computes fishing conditions per location and day.
5. Writes a styled `index.html` grouped by date with a legend and per-row condition badge.

---

## Sample Output

```
Location        Date                   Sunrise  Summary                                  Temp (°F)    Pressure (inHg)  Wind Speed (mph)  Wind Gust (mph)  Fishing                       
--------------------------------------------------------------------------------------------------------------------------------------------------------------
Winnipesaukee   Saturday 06-05-2025    05:09    partly cloudy with rain                63.81        29.88             12.55             17.05             Lite Wind (Gusty, Low Pressure)
Winnipesaukee   Sunday 06-06-2025      05:09    clear sky                                 71.91        30.12             4.41              6.22              Lite Wind (Comfortable Temp, High Pressure)
Newfound        Saturday 06-05-2025    05:12    mostly sunny                              65.10        29.95             7.30              9.50              Moderate Wind (Comfortable Temp, High Pressure)
... (additional rows for each lake & date)
```

---

## Automating Updates

If you want periodic updates:

1. **GitHub Actions**

   - Create a workflow that:
     1. Checks out the repo
     2. Installs Python and `requests`
     3. Runs `python fishing.py`
     4. Commits the generated `index.html` in your chosen `output_dir`
   - Consider pointing `output_dir` to a `docs/` folder in your repo and enable GitHub Pages to serve from `docs`.

2. **Local cron job**

   - Example crontab entry (hourly):

     ```
     0 * * * * /path/to/venv/bin/python /path/to/fishing.py >> /path/to/fishing.log 2>&1
     ```

---

## Logging

Structured logging is enabled. Control verbosity with the `LOG_LEVEL` environment variable (`DEBUG`, `INFO`, `WARNING`, `ERROR`).

- macOS/Linux (zsh/bash):

  ```bash
  LOG_LEVEL=DEBUG python fishing.py
  ```

- PowerShell:

  ```powershell
  $env:LOG_LEVEL='DEBUG'; python fishing.py
  ```

---

## Optional: Push Results to Google Sheets

If you prefer hosting in a Google Sheet and embedding in Google Sites:

1. **Enable Google Sheets API**

   * In Google Cloud Console, enable “Google Sheets API.”
   * Create a Service Account (JSON key), name it e.g. `gcp-sa-credentials.json`.
   * Share your target Google Sheet with the service-account email.

2. **Install dependencies**:

   ```bash
   pip install gspread google-auth
   ```

3. **Add to `fishing.py`** (after building `all_rows`):

   ```python
   import gspread
   from google.oauth2.service_account import Credentials

   SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
   creds = Credentials.from_service_account_file("gcp-sa-credentials.json", scopes=SCOPES)
   gc = gspread.authorize(creds)

   SPREADSHEET_ID = "YOUR_SPREADSHEET_ID"
   sh = gc.open_by_key(SPREADSHEET_ID)
   try:
       ws = sh.worksheet("Forecast")
   except gspread.WorksheetNotFound:
       ws = sh.add_worksheet(title="Forecast", rows="100", cols="20")

   header = ["Location","Date","Sunrise","Summary","Temp (°F)","Pressure (inHg)","Wind Speed (mph)","Wind Gust (mph)","Fishing"]
   values = [header]
   for row in all_rows:
       values.append([
           row["location"],
           row["date_str"],
           row["sunrise"],
           row["summary"],
           row["temp"],
           row["pressure"],
           row["wind_speed"],
           row["wind_gust"],
           row["fishing"],
       ])

   ws.clear()
   ws.update("A1", values)
   print("Pushed forecast to Google Sheets.")
   ```

4. Run the script each hour (cron/Action). The embedded Sheet in Google Sites (or shared link) will automatically reflect the latest data.

---

## Tips & Troubleshooting

* **HTTP 401 Unauthorized**: Ensure your OpenWeatherMap API key is valid and has One Call permissions.
* **Missing Data**: If a field (e.g. `wind_gust`) is absent, the script defaults it to `0`. Adjust logic if needed.
* **Empty or Invalid `settings.json`**: Make sure every location has both `"lat"` and `"lon"` as strings or numbers.
* **GitHub Actions Failing**: Check that your repository includes `config.json` (with a valid key) and, if using Sheets, `gcp-sa-credentials.json` (set as a secret).
* **Table Alignment**: The script uses fixed-width f-strings (e.g. `:<18`). If numeric values have varying lengths, columns may shift slightly. Adjust widths to your preference.

---

## License

This project is released under the MIT License. See [LICENSE](LICENSE) for details.

---

Feel free to adapt thresholds, add or remove lakes, and extend the script (e.g. push to CSV, send an email alert if “Absolutely no fishing” occurs, etc.). Tight lines and happy coding!
