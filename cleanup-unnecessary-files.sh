#!/bin/bash

# Cleanup script to remove unnecessary files from the repository
# This script removes redundant documentation, old scripts, and temporary files

echo "🧹 Cleaning up unnecessary files from repository..."

# Create backup directory for any files we might want to keep
mkdir -p backups/cleanup-$(date +%Y%m%d_%H%M%S)

# Function to safely remove files with backup
safe_remove() {
    local file="$1"
    local reason="$2"
    
    if [ -f "$file" ]; then
        echo "🗑️  Removing: $file ($reason)"
        mv "$file" "backups/cleanup-$(date +%Y%m%d_%H%M%S)/"
    fi
}

# Function to safely remove directories
safe_remove_dir() {
    local dir="$1"
    local reason="$2"
    
    if [ -d "$dir" ]; then
        echo "🗑️  Removing directory: $dir ($reason)"
        mv "$dir" "backups/cleanup-$(date +%Y%m%d_%H%M%S)/"
    fi
}

echo "📋 Analyzing files for cleanup..."

# 1. Remove redundant documentation files
echo ""
echo "📚 Removing redundant documentation files..."
safe_remove "REPOSITORY_CLEANUP.md" "Redundant with PRODUCTION_WORKFLOW.md"
safe_remove "SHELL_SCRIPTS.md" "Redundant with PRODUCTION_WORKFLOW.md"
safe_remove "QUICK_UPDATE.md" "Redundant with PRODUCTION_WORKFLOW.md"
safe_remove "UPDATE_GUIDE.md" "Redundant with PRODUCTION_WORKFLOW.md"
safe_remove "ENHANCED_FISHING_ANALYSIS.md" "Redundant documentation"
safe_remove "PRODUCTION_DEPLOYMENT.md" "Redundant with PRODUCTION_WORKFLOW.md"
safe_remove "ROCKY_LINUX_QUICK_START.md" "Redundant with PRODUCTION_WORKFLOW.md"
safe_remove "WEB_SERVER_CONFIG.md" "Redundant with PRODUCTION_WORKFLOW.md"
safe_remove "SSL_SETUP.md" "Redundant with PRODUCTION_WORKFLOW.md"

# 2. Remove old/duplicate scripts
echo ""
echo "🔧 Removing old/duplicate scripts..."
safe_remove "update-deployment.sh" "Replaced by git-workflow.sh"
safe_remove "fix-ssl-config.sh" "Functionality integrated into setup-production.sh"
safe_remove "setup-production.sh" "Replaced by deploy-production.sh"

# 3. Remove old backup files (keep only the most recent)
echo ""
echo "💾 Cleaning up old backup files..."
if [ -d "backups" ]; then
    # Keep only the 3 most recent database backups
    cd backups
    ls -t weather_data_*.db 2>/dev/null | tail -n +4 | xargs -r rm -f
    cd ..
    
    # Remove old cleanup backups (keep only the most recent)
    if [ -d "backups/cleanup" ]; then
        cd backups/cleanup
        ls -t *.backup 2>/dev/null | tail -n +2 | xargs -r rm -f
        cd ../..
    fi
fi

# 4. Remove Python cache files
echo ""
echo "🐍 Removing Python cache files..."
safe_remove_dir "__pycache__" "Python cache directory"
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# 5. Remove empty database file (it will be recreated when needed)
echo ""
echo "🗄️  Removing empty database file..."
if [ -f "weather_data.db" ] && [ ! -s "weather_data.db" ]; then
    safe_remove "weather_data.db" "Empty database file (will be recreated)"
fi

# 6. Remove the cleanup script itself (after running)
echo ""
echo "🧹 This cleanup script will remove itself after completion..."

# 7. Update .gitignore to prevent future clutter
echo ""
echo "📝 Updating .gitignore..."
cat >> .gitignore << 'EOF'

# Additional cleanup
*.pyc
*.pyo
__pycache__/
*.log
*.tmp
*.swp
*.swo
*~

# IDE files
.vscode/
.idea/
*.sublime-*

# OS files
.DS_Store
Thumbs.db
EOF
