#!/bin/bash

# Fishing Weather Portal - Update Deployment Script
# This script updates the fishing weather portal on Rocky Linux

echo "🔄 Updating Fishing Weather Portal..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the fishing-weather directory."
    exit 1
fi

# Step 1: Backup current database
echo "💾 Backing up database..."
./backup-database.sh

# Step 2: Pull latest changes
echo "📥 Pulling latest changes from Git..."
git pull origin main

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to pull latest changes from Git"
    exit 1
fi

# Step 3: Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Step 4: Update dependencies
echo "📦 Updating dependencies..."
pip install -r requirements.txt

# Step 5: Update static files
echo "🌐 Updating static files..."
WEB_DIR="/var/www/fishing.thepeaveys.net/public_html"

# Backup current static files
sudo cp -r "$WEB_DIR" "${WEB_DIR}.backup.$(date +%Y%m%d_%H%M%S)"

# Copy new static files
sudo cp -r fishing-website/* "$WEB_DIR/"

# Set proper permissions
sudo chown -R $USER:$USER "$WEB_DIR"
sudo chmod -R 755 "$WEB_DIR"

# Step 6: Test the deployment
echo "🧪 Testing deployment..."
python3 test_deployment.py

if [ $? -ne 0 ]; then
    echo "❌ Deployment test failed. Rolling back..."
    sudo rm -rf "$WEB_DIR"
    sudo mv "${WEB_DIR}.backup.$(date +%Y%m%d_%H%M%S)" "$WEB_DIR"
    echo "✅ Rollback complete. Please check the errors and try again."
    exit 1
fi

# Step 7: Restart the application
echo "🔄 Restarting application..."
sudo systemctl restart fishing-weather

# Step 8: Check status
echo "📊 Checking application status..."
sleep 3
if sudo systemctl is-active --quiet fishing-weather; then
    echo "✅ Application restarted successfully"
else
    echo "❌ Application failed to restart"
    sudo systemctl status fishing-weather
    exit 1
fi

# Step 9: Test the application
echo "🧪 Testing application..."
sleep 2
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ Application is responding"
else
    echo "⚠️  Application may not be fully ready yet"
fi

echo ""
echo "🎉 Update deployment successful!"
echo ""
echo "📁 Updated directories:"
echo "   Code: $(pwd)"
echo "   Web: $WEB_DIR"
echo "   Database: $(pwd)/weather_data.db (backed up)"
echo ""
echo "🌐 Your portal is available at:"
echo "   http://fishing.thepeaveys.net"
echo ""
echo "📊 Check application status:"
echo "   sudo systemctl status fishing-weather"
echo ""
echo "📝 View logs:"
echo "   sudo journalctl -u fishing-weather -f"
echo ""
echo "🎣 Happy fishing!"
