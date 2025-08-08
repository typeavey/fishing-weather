#!/bin/bash
cd "$(dirname "$0")"
BACKUP_DIR="backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/weather_data_$TIMESTAMP.db"
cp weather_data.db "$BACKUP_FILE"
echo "✅ Database backed up to: $BACKUP_FILE"
