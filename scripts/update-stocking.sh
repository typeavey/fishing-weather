#!/bin/bash
# Stocking Data Update Script
# Updates fish stocking data from NH Fish & Game

# Set the website directory
WEBSITE_DIR="/var/www/fishing.thepeaveys.net/public_html"
cd "$WEBSITE_DIR" || exit 1

# Set up logging
LOG_DIR="$HOME/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/stocking_update.log"

echo "$(date): 🎣 Starting stocking data update..." >> "$LOG_FILE"

        # Check if Python script exists
        if [ ! -f "scripts/stocking_data.py" ]; then
    echo "$(date): ❌ stocking_data.py not found" >> "$LOG_FILE"
    exit 1
fi

        # Run the stocking update
        echo "$(date): 📊 Running stocking data update..." >> "$LOG_FILE"
        python3 scripts/stocking_data.py >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "$(date): ✅ Stocking data update completed successfully" >> "$LOG_FILE"
else
    echo "$(date): ❌ Stocking data update failed" >> "$LOG_FILE"
fi

echo "$(date): 🏁 Stocking update script finished" >> "$LOG_FILE"
