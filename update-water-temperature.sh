#!/bin/bash

# Water Temperature Update Script
# Automatically updates water temperature data from USGS and NOAA

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/water_temperature_update.log"
LOCK_FILE="$SCRIPT_DIR/water_temperature_update.lock"

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

# Error logging function
log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

# Success logging function
log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1" | tee -a "$LOG_FILE"
}

# Warning logging function
log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

# Check if script is already running
if [ -f "$LOCK_FILE" ]; then
    PID=$(cat "$LOCK_FILE" 2>/dev/null)
    if ps -p "$PID" > /dev/null 2>&1; then
        log_error "Update script is already running (PID: $PID)"
        exit 1
    else
        log_warning "Removing stale lock file"
        rm -f "$LOCK_FILE"
    fi
fi

# Create lock file
echo $$ > "$LOCK_FILE"

# Cleanup function
cleanup() {
    rm -f "$LOCK_FILE"
    log "Water temperature update script completed"
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Main update function
update_water_temperatures() {
    log "Starting water temperature update..."
    
    # Change to script directory
    cd "$SCRIPT_DIR"
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        log "Activating virtual environment..."
        source venv/bin/activate
    fi
    
    # Run the water temperature update
    log "Running water temperature update..."
    python3 -c "
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))
from water_temperature import WaterTemperatureData

try:
    water_temp = WaterTemperatureData()
    result = water_temp.update_water_temperatures()
    print(f'Update result: {result}')
    if result['success']:
        print(f'Records updated: {result[\"records_updated\"]}')
        print(f'Sources used: {result[\"sources_used\"]}')
    else:
        print(f'Error: {result.get(\"error\", \"Unknown error\")}')
        sys.exit(1)
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        log_success "Water temperature update completed successfully"
    else
        log_error "Water temperature update failed"
        return 1
    fi
}

# Check current status
check_status() {
    log "Checking current water temperature status..."
    
    cd "$SCRIPT_DIR"
    
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    python3 -c "
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))
from water_temperature import WaterTemperatureData

try:
    water_temp = WaterTemperatureData()
    latest = water_temp.get_latest_temperatures()
    print('Latest water temperatures:')
    for lake, data in latest.items():
        print(f'{lake}: {data[\"temperature_celsius\"]}°C ({data[\"temperature_fahrenheit\"]}°F) - {data[\"source\"]}')
except Exception as e:
    print(f'Error checking status: {e}')
"
}

# Test data sources
test_sources() {
    log "Testing water temperature data sources..."
    
    cd "$SCRIPT_DIR"
    
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    python3 -c "
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))
from water_temperature import WaterTemperatureData

try:
    water_temp = WaterTemperatureData()
    
    # Test USGS
    print('Testing USGS data...')
    usgs_record = water_temp.fetch_usgs_temperature('Champlain')
    if usgs_record:
        print(f'USGS Champlain: {usgs_record.temperature_celsius}°C ({usgs_record.temperature_fahrenheit}°F)')
    else:
        print('USGS data not available')
    
    # Test NOAA
    print('Testing NOAA data...')
    noaa_record = water_temp.fetch_noaa_temperature('Champlain')
    if noaa_record:
        print(f'NOAA Champlain: {noaa_record.temperature_celsius}°C ({noaa_record.temperature_fahrenheit}°F)')
    else:
        print('NOAA data not available')
    
    # Test estimation
    print('Testing estimation...')
    import datetime
    estimated = water_temp.estimate_temperature('Winnipesaukee', 22.0, datetime.date.today())
    print(f'Estimated Winnipesaukee: {estimated.temperature_celsius}°C ({estimated.temperature_fahrenheit}°F)')
    
except Exception as e:
    print(f'Error testing sources: {e}')
"
}

# Main script logic
main() {
    log "=== Water Temperature Update Script ==="
    
    # Check if we're in the right directory
    if [ ! -f "water_temperature.py" ]; then
        log_error "water_temperature.py not found. Please run this script from the fishing-weather directory."
        exit 1
    fi
    
    # Parse command line arguments
    case "${1:-update}" in
        "update")
            update_water_temperatures
            ;;
        "status")
            check_status
            ;;
        "test")
            test_sources
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  update  - Update water temperature data from USGS and NOAA (default)"
            echo "  status  - Check current water temperature status"
            echo "  test    - Test the water temperature data sources"
            echo "  help    - Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0              # Update water temperatures"
            echo "  $0 status       # Check status"
            echo "  $0 test         # Test data sources"
            ;;
        *)
            log_error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
