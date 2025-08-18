#!/bin/bash
# Weather Data Update Script
# Updates weather data from OpenWeatherMap API

# Set the website directory
WEBSITE_DIR="/var/www/fishing.thepeaveys.net/public_html"
cd "$WEBSITE_DIR" || exit 1

# Set up logging
LOG_DIR="$HOME/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/weather_update.log"

echo "$(date): 🌤️ Starting weather data update..." >> "$LOG_FILE"

        # Check if Python script exists
        if [ ! -f "scripts/update_weather_data.py" ]; then
    echo "$(date): ❌ update_weather_data.py not found" >> "$LOG_FILE"
    exit 1
fi

# Check if API key is set
if [ -z "$OPENWEATHER_API_KEY" ]; then
    echo "$(date): ❌ OPENWEATHER_API_KEY not set" >> "$LOG_FILE"
    echo "$(date): 💡 Please set your API key: export OPENWEATHER_API_KEY='your_key'" >> "$LOG_FILE"
    exit 1
fi

        # Run the weather update
        echo "$(date): 📊 Running weather data update..." >> "$LOG_FILE"
        python3 scripts/update_weather_data.py >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "$(date): ✅ Weather data update completed successfully" >> "$LOG_FILE"
else
    echo "$(date): ❌ Weather data update failed" >> "$LOG_FILE"
fi

echo "$(date): 🏁 Weather update script finished" >> "$LOG_FILE"
