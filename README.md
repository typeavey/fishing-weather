# Fishing Forecast Automation

This repository contains a Python script that fetches 8-day weather forecasts for multiple lakes, evaluates “fishing conditions” based on configurable thresholds (wind, temperature, pressure), and prints a combined, date-sorted table to the console. You can also adapt it to push results to Google Sheets or deploy to GitHub Pages as a static HTML page.

---

## Contents

* **`fetch_forecast.py`**
  Main Python script that reads API credentials and settings, retrieves weather data from OpenWeatherMap’s One Call API, computes “fishing” status, and outputs a formatted table.

* **`config.json`**
  Contains a single field:

  ```json
  {
    "api_key": "YOUR_OPENWEATHERMAP_API_KEY"
  }
  ```

  * **`api_key`**: Your OpenWeatherMap API key (One Call 3.0 must be enabled on your account).

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

1. **Python 3.8+** (tested on 3.10 and 3.11)
2. **PIP** (for installing dependencies)
3. **An OpenWeatherMap API key** (One Call API 3.0 enabled).

   * Sign up at [https://openweathermap.org/](https://openweathermap.org/) and enable the One Call 3.0 subscription.

---

## Installation

1. **Clone this repository**:

   ```bash
   git clone https://github.com/<your-username>/fishing-forecast.git
   cd fishing-forecast
   ```

2. **Create a virtual environment (recommended)**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate      # macOS/Linux
   # venv\Scripts\activate.bat   # Windows
   ```

3. **Install required packages**:

   ```bash
   pip install requests
   ```

---

## Configuration

1. **Populate `config.json`**
   Rename the placeholder or edit directly:

   ```json
   {
     "api_key": "YOUR_OPENWEATHERMAP_API_KEY"
   }
   ```

   Replace `"YOUR_OPENWEATHERMAP_API_KEY"` with your actual key.

2. **Customize `settings.json`**

   * Add or remove locations under `"locations"`.
   * Adjust threshold values under `"thresholds"`.
   * Ensure all numeric values (wind, gust, temp, pressure) match the units (mph for winds, °F for temp, inHg for pressure).

---

## Usage

Run the forecast script:

```bash
python fetch_forecast.py
```

This will:

1. Load your OpenWeatherMap API key from `config.json`.

2. Load your set of locations and threshold rules from `settings.json`.

3. Call the One Call 3.0 API for each lake’s latitude/longitude.

4. Build and sort an array of rows containing:

   * **Location**
   * **Date** (e.g. `Saturday 06-05-2025`)
   * **Sunrise** time
   * **Weather summary** (truncated if > 40 chars)
   * **Day temperature** (°F)
   * **Barometric pressure** (converted from hPa → inHg)
   * **Wind speed** (mph)
   * **Wind gust** (mph)
   * **Fishing** (base label + appended notes for gusts, temp, pressure)

5. Print a combined table, sorted by date, with the above columns.

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

## Automating Hourly Updates

If you want hourly updates without manual intervention, you can:

1. **GitHub Actions (recommended)**

   * Create a workflow `.github/workflows/auto-update.yml` that:

     1. Checks out the repo.
     2. Installs Python and dependencies.
     3. Runs `fetch_forecast.py` to regenerate `index.html` (see optional step below).
     4. **(Optional)** Commits newly generated HTML → `gh-pages` branch.
   * **Skip commits if unchanged** (use a `git diff --quiet` check) or use `git commit --amend` + `--force` to keep a single-commit history.

2. **Local cron job**

   * Install `cron` on your machine/server.
   * Create a `crontab -e` entry:

     ```
     0 * * * * /path/to/venv/bin/python /path/to/fetch_forecast.py >> /path/to/fetch.log 2>&1
     ```
   * This runs at the top of every hour, updating your console output or (if you extend to write HTML/Sheets) refreshing wherever you publish.

---

## Optional: Generate a Static HTML Page

Instead of printing to console, you can modify `fetch_forecast.py` to create `index.html`:

1. Build a list of table rows (`<tr>…</tr>`) inside your script.
2. Wrap them in a basic HTML template:

   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
     <meta charset="UTF-8" />
     <meta name="viewport" content="width=device-width, initial-scale=1.0" />
     <title>Fishing Forecast</title>
     <style>
       table { border-collapse: collapse; width: 100%; }
       th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
       th { background-color: #f2f2f2; }
     </style>
   </head>
   <body>
     <h1>8-Day Fishing Forecast</h1>
     <table>
       <thead>
         <tr>
           <th>Location</th><th>Date</th><th>Sunrise</th><th>Summary</th>
           <th>Temp (°F)</th><th>Pressure (inHg)</th>
           <th>Wind Speed (mph)</th><th>Wind Gust (mph)</th><th>Fishing</th>
         </tr>
       </thead>
       <tbody>
         <!-- Insert rows_html here -->
       </tbody>
     </table>
   </body>
   </html>
   ```
3. Write it to `index.html` instead of printing.
4. Commit/push `index.html` to a `gh-pages` branch (or `/docs` folder on `main`).
5. Enable GitHub Pages (Settings → Pages) to serve from `gh-pages` (root) or `main/docs`.

   * Site URL: `https://<your-username>.github.io/fishing-forecast/`.

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

3. **Add to `fetch_forecast.py`** (after building `all_rows`):

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
