### Project: NH‑VT Trolling Conditions (Fishing Weather Website)

This site presents fishing‑relevant weather intelligence for lakes in NH/VT. It combines a small Flask API that serves data from SQLite databases with static HTML pages styled by a shared CSS and powered by lightweight JavaScript utilities. Background scripts periodically fetch and store fresh data (weather, stocking, water temperature) into SQLite.

**Current Status**: Production-ready with automated data updates, comprehensive security, and optimized performance.

---

### What the website is
- **Goal**: Help anglers quickly assess current conditions and plan trips.
- **Core features**:
  - Current weather and fishing conditions (dashboard + detailed pages)
  - Forecasts
  - Locations directory
  - Analysis/guide content
  - Fish stocking information
- **Tech stack**: Flask (Python) for API, static HTML/CSS/JS for UI, SQLite for storage, cron/shell scripts + Python updaters for data ingestion.
- **Security**: Comprehensive .gitignore protection, environment-based API keys, no hardcoded secrets
- **Automation**: Hourly weather updates via cron, daily stocking/water temp updates

---

### How it works (data flow)
1. **Fetch**: Background scripts in `public_html/scripts/` call external APIs or scrape sources (e.g., OpenWeatherMap, USGS, NH Fish & Game) and write normalized rows into SQLite databases under `public_html/sqlite_db/`. Weather data updates hourly, other data updates daily.
2. **Store**: Databases:
   - `weather_data.db` → weather + derived fishing metrics
   - `water_temperature.db` → lake water temps (measured/estimated)
   - `stocking_data.db` → stocking records
3. **Serve**: `app.py` (Flask) exposes REST endpoints that read from those SQLite DBs and return JSON.
4. **Display**: Static pages (e.g., `index.html`, `weather.html`) fetch API JSON and render in the browser using small utility functions in `js/utils.js`. Styling is centralized in `css/shared.css`.

---

### Runtime components
- **Flask API**: `public_html/app.py`
  - Runs with Python 3.9+ and `flask`, `flask_cors`.
  - Serves HTML files and static `css`/`js` directly.
  - Adds `scripts/` to `sys.path` to import shared DB helpers.
- **Databases**: `public_html/sqlite_db/*.db`
- **Background jobs**: shell scripts in `public_html/scripts/` designed to be run via cron (or manually) to keep data current.
- **Security**: All sensitive files (logs, databases, configs) are gitignored and protected

---

### API endpoints (served by `app.py`)
- `GET /api/weather` — Latest weather rows (ORDER BY created_at DESC, limited)
- `GET /api/forecast` — Recent/near‑term forecast rows (time‑filtered, limited)
- `GET /api/locations` — Static list of lake locations (lat/lon, names)
- `GET /api/stocking` — Stocking records (limited)
- `GET /api/water-temperature` — Recent water temperature rows (limited)
- `GET /api/water-temperature/latest` — Most recent temperature per lake (dictionary keyed by lake)
- Also includes temporary/utility cleanup endpoints (if present in file) that rely on `WorkingWeatherDatabase`.

The Flask app also routes each HTML (e.g., `/weather.html`) and serves static `/css/...` and `/js/...` files.

---

### Front‑end pages (static HTML)
- `index.html` — Dashboard landing page. Shows:
  - Dashboard cards linking to Weather, Forecast, Locations, Analysis, Guide, Stocking
  - “Current Weather & Fishing Conditions” module with filters and a table/card view fed by `/api/weather`
  - Uses shared CSS/JS (`css/shared.css`, `js/utils.js`)
  - Features: Chronologically sorted day filters, deduplicated data display, consistent table layout
  - Note: The separate water temperature dashboard section was removed intentionally; water temp is still available via API and dedicated pages.
- `weather.html` — Rich, card‑based current conditions view with optional synthesis info and integration of water temp where applicable.
- `forecast.html` — Forecast‑focused page (8‑day window).
- `locations.html` — List of supported lakes/places.
- `analysis.html` — Explanations of fishing‑relevant metrics and interpretive content.
- `guide.html` — User‑oriented guide for reading the site (headers/styles aligned to dashboard).
- `stocking.html` — Fish stocking records view.
- `debug_weather.html`, `debug_dashboard.html` — Lightweight diagnostic pages used during troubleshooting (safe to remove in production).

All pages rely on:
- `css/shared.css` — Shared tokens, layout, header/nav styles, responsive rules
- `js/utils.js` — Fetch helpers, rating utilities, simple DOM helpers

Optional/legacy:
- `js/weather-api.js` — Older/auxiliary client logic (may be partially superseded by `utils.js`).

---

### Scripts (ingestion and automation)
Located in `public_html/scripts/`:
- `update_weather_data.py` — Fetches current weather and forecast from OpenWeatherMap (requires `OPENWEATHER_API_KEY` env var) and writes rows to `../sqlite_db/weather_data.db`.
- `water_temperature.py` — Gathers water temperatures (from USGS when available, otherwise estimates) and writes to `../sqlite_db/water_temperature.db`.
- `stocking_data.py` — Scrapes/parses stocking records into `../sqlite_db/stocking_data.db`.
- `working_database.py` — Shared helper class for SQLite operations (schema management, cleanup, convenience methods).
- `update-weather.sh` — Non‑interactive shell wrapper to run the weather updater and log output to `~/logs/weather_update.log`.
- `update-water-temperature.sh` — Wrapper for water temp updater, logs to `~/logs/water_temperature_update.log`.
- `update-stocking.sh` — Wrapper for stocking updater, logs to `~/logs/stocking_update.log`.

These shell scripts are designed to be used with cron (e.g., hourly for weather at the top of each hour, daily for stocking) and are safe to run manually. They assume the working directory is `public_html/` and Python 3 is available as `python3`.

---

### Databases and schemas (SQLite)
- `sqlite_db/weather_data.db` — Weather rows include fields like `location`, `date_str`, `date_ts`, `temp`, `wind_speed`, `pressure`, `summary`, and derived `fishing_base` rating. API sorts by `created_at` (or time fields) to return freshest data first.
- `sqlite_db/water_temperature.db` — Table `water_temperature_records` with columns like `lake_name`, `temperature_celsius`, `temperature_fahrenheit`, `timestamp`, `source`, optional geospatial metadata, `depth`, and `notes`.
- `sqlite_db/stocking_data.db` — Stocking records (species, counts, dates, locations).

Schemas are managed by the Python updaters and helper classes in `working_database.py` (create tables if missing and migrate as needed).

---

### Running and deploying
- From `public_html/`, run the API server:
  - `python3 app.py` (writes logs to `app.log`)
- The site is designed to be reverse‑proxied (or accessed directly on Flask’s port in development). For production, a WSGI server (gunicorn/uwsgi) is recommended.
- Ensure Python packages from `requirements.txt` are installed in the environment. Key packages: `flask`, `flask_cors`, `requests` (for updaters), etc.

Environment/config:
- `OPENWEATHER_API_KEY` must be set for `update_weather_data.py`.
- Cron should call the shell wrappers in `scripts/`. Logs are written under `~/logs/`.

Security:
- Comprehensive `.gitignore` protects sensitive files (logs, databases, configs)
- API keys are environment-based, never hardcoded
- All sensitive data is excluded from version control
- See `SECURITY.md` for detailed security documentation

---

### Troubleshooting pointers
- If API responds but dashboard shows no data:
  - Check browser console for JS errors (enhanced debugging is now in place)
  - Verify `/js/utils.js` and `/css/shared.css` are served (Flask routes exist in `app.py`)
  - Confirm `/api/weather` returns rows (curl)
  - Verify updaters are writing to the same DB files the API reads (`sqlite_db/*`)
- If imports fail in `app.py` for DB helpers, confirm `sys.path` includes `scripts/` (this file appends it).
- If data looks stale, run shell updaters manually and tail logs in `~/logs/`.
- If you see duplicate rows, the deduplication logic should handle this automatically.
- Weather updates now run hourly at the top of each hour (check cron jobs with `crontab -l`).

---

### File‑by‑file reference (public_html)
- `app.py` — Flask API server; defines REST endpoints, serves HTML pages, and static `/css` & `/js`. Adds `scripts/` to `sys.path` to import `working_database`.
- `index.html` — Dashboard landing page; fetches `/api/weather` via `js/utils.js`, renders filters + table/cards.
- `weather.html` — Detailed weather/cards page; integrates water temp where applicable.
- `forecast.html` — Forecast presentation using `/api/forecast`.
- `locations.html` — Fishing locations directory and quick info.
- `analysis.html` — Deeper explanations and rationale behind the ratings and metrics.
- `guide.html` — User guide for interpreting the site; header styling consistent with dashboard.
- `stocking.html` — Stocking data UI.
- `css/shared.css` — Site‑wide CSS tokens and UI components (header/nav, grids, modules, responsive rules).
- `js/utils.js` — Shared JS utilities:
  - `fetchData(endpoint)` wrapper
  - `loadWeatherData()`, `loadWaterTemperatureData()`, `loadStockingData()`
  - Rating helpers: `getFishingRating`, `getRatingColor`, `getRatingExplanation`
  - DOM helpers and simple loading/error states
  - Date/time formatting helpers
- `js/weather-api.js` — Auxiliary/legacy client logic (may overlap with `utils.js`).
- `sqlite_db/weather_data.db` — Weather data SQLite DB.
- `sqlite_db/water_temperature.db` — Water temperature SQLite DB.
- `sqlite_db/stocking_data.db` — Stocking data SQLite DB.
- `scripts/update_weather_data.py` — Weather/forecast ingester (uses `OPENWEATHER_API_KEY`).
- `scripts/water_temperature.py` — Water temperature ingester (USGS + estimation).
- `scripts/stocking_data.py` — Stocking records ingester.
- `scripts/working_database.py` — SQLite helper class used by scripts and occasionally API cleanup.
- `scripts/update-weather.sh` — Wrapper to run weather ingester, logs to `~/logs/weather_update.log`.
- `scripts/update-water-temperature.sh` — Wrapper for water temp ingester.
- `scripts/update-stocking.sh` — Wrapper for stocking ingester.
- `app.log` — Runtime log for Flask server (stdout/stderr via nohup or direct run).
- `requirements.txt` — Python dependencies.
- `README.md` — Human documentation for general setup/usage.
- `debug_weather.html`, `debug_dashboard.html` — Diagnostic/test pages (optional).
- `SECURITY.md` — Comprehensive security documentation and best practices.
- `.gitignore` — Protects sensitive files from version control.

---

### Recent Improvements & Current Features

**Dashboard Enhancements:**
- Consistent table layout (no more switching between cards/table)
- Chronologically sorted day filters (oldest to newest)
- Data deduplication (prevents duplicate rows for same lake+date)
- Enhanced error handling and debugging

**Data Management:**
- Hourly weather updates (top of each hour) instead of every 15 minutes
- Automatic cleanup of old weather data (30+ days)
- Robust error handling in update scripts
- Comprehensive logging to `~/logs/` directory

**Security & Best Practices:**
- Environment-based API key management
- Comprehensive `.gitignore` protection
- No hardcoded secrets or credentials
- Production-ready security configuration

**Performance Optimizations:**
- Efficient data filtering and display
- Optimized API endpoints with proper sorting
- Shared utility functions for consistent behavior
- Responsive design with mobile optimization

---

### Notes for AI agents
- Prefer the API for data access; do not read SQLite files directly unless you are debugging.
- When adding new scripts or endpoints, keep DB paths consistent with `sqlite_db/` and update callers accordingly.
- If you reorganize files, ensure `app.py` continues to serve `/css` and `/js` and that `scripts/` remains importable (path append).
- For scheduled tasks, call the existing shell wrappers non‑interactively (cron safe) and write logs under `~/logs/`.
