#!/bin/bash
# Water Temperature Update Script
# Updates water temperature data from USGS and NOAA

# Set the website directory
WEBSITE_DIR="/var/www/fishing.thepeaveys.net/public_html"
cd "$WEBSITE_DIR" || exit 1

# Set up logging
LOG_DIR="$HOME/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/water_temperature_update.log"

echo "$(date): 🌡️ Starting water temperature update..." >> "$LOG_FILE"

        # Check if Python script exists
        if [ ! -f "scripts/water_temperature.py" ]; then
    echo "$(date): ❌ water_temperature.py not found" >> "$LOG_FILE"
    exit 1
fi

        # Run the water temperature update
        echo "$(date): 📊 Running water temperature update..." >> "$LOG_FILE"
        python3 scripts/water_temperature.py >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "$(date): ✅ Water temperature update completed successfully" >> "$LOG_FILE"
else
    echo "$(date): ❌ Water temperature update failed" >> "$LOG_FILE"
fi

echo "$(date): 🏁 Water temperature update script finished" >> "$LOG_FILE"
