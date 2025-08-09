#!/bin/bash

# Stocking Data Update Script
# Automatically updates stocking data from NH Fish & Game

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/stocking_update.log"
LOCK_FILE="$SCRIPT_DIR/stocking_update.lock"

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
    log "Update script completed"
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Main update function
update_stocking_data() {
    log "Starting stocking data update..."
    
    # Change to script directory
    cd "$SCRIPT_DIR"
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        log "Activating virtual environment..."
        source venv/bin/activate
    fi
    
    # Run the stocking data update
    log "Running stocking data update..."
    python3 -c "
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))
from stocking_data import NHStockingData

try:
    stocking_data = NHStockingData()
    result = stocking_data.update_stocking_data()
    print(f'Update result: {result}')
    if result['success']:
        print(f'Records updated: {result[\"records_updated\"]}')
        print(f'Source: {result[\"source\"]}')
    else:
        print(f'Error: {result.get(\"error\", \"Unknown error\")}')
        sys.exit(1)
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        log_success "Stocking data update completed successfully"
    else
        log_error "Stocking data update failed"
        return 1
    fi
}

# Check current status
check_status() {
    log "Checking current stocking data status..."
    
    cd "$SCRIPT_DIR"
    
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    python3 -c "
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))
from stocking_data import NHStockingData

try:
    stocking_data = NHStockingData()
    status = stocking_data.get_update_status()
    print(f'Last update: {status[\"last_update\"]}')
    print(f'Records updated: {status[\"records_updated\"]}')
    print(f'Success: {status[\"success\"]}')
    if not status['success']:
        print(f'Error: {status[\"error_message\"]}')
except Exception as e:
    print(f'Error checking status: {e}')
"
}

# Main script logic
main() {
    log "=== Stocking Data Update Script ==="
    
    # Check if we're in the right directory
    if [ ! -f "stocking_data.py" ]; then
        log_error "stocking_data.py not found. Please run this script from the fishing-weather directory."
        exit 1
    fi
    
    # Parse command line arguments
    case "${1:-update}" in
        "update")
            update_stocking_data
            ;;
        "status")
            check_status
            ;;
        "test")
            log "Testing stocking data module..."
            python3 stocking_data.py
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  update  - Update stocking data from NH Fish & Game (default)"
            echo "  status  - Check current stocking data status"
            echo "  test    - Test the stocking data module"
            echo "  help    - Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0              # Update stocking data"
            echo "  $0 status       # Check status"
            echo "  $0 test         # Test module"
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
