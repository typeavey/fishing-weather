#!/bin/bash

# Fishing Weather Portal - Production Deployment Script
# This script deploys the fishing weather portal to production
# Configured for Rocky Linux with code in /home/typeavey/fishing-weather
# and web server serving from /var/www/fishing.thepeaveys.net/public_html

echo "🚀 Deploying Fishing Weather Portal to Production..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the fishing-weather directory."
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    echo "   Please install Python 3.9+ first:"
    echo "   sudo dnf install -y python3 python3-pip python3-devel"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if database exists
if [ ! -f "weather_data.db" ]; then
    echo "🗄️ Initializing SQLite database..."
    python3 working_database.py
fi

# Create web directory if it doesn't exist
WEB_DIR="/var/www/fishing.thepeaveys.net/public_html"
echo "🌐 Setting up web directory: $WEB_DIR"

# Create web directory and copy static files
sudo mkdir -p "$WEB_DIR"
sudo cp -r fishing-website/* "$WEB_DIR/"
sudo chown -R $USER:$USER "$WEB_DIR"
sudo chmod -R 755 "$WEB_DIR"

# Create symbolic link for easy updates
echo "🔗 Creating symbolic link for easy updates..."
sudo ln -sf "$(pwd)/fishing-website" "$WEB_DIR/fishing-website"

# Test the deployment
echo "🧪 Testing deployment..."
python3 test_deployment.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Production deployment successful!"
    echo ""
    echo "📁 Directory Structure:"
    echo "   Code: $(pwd)"
    echo "   Web: $WEB_DIR"
    echo "   Database: $(pwd)/weather_data.db"
    echo ""
    echo "🚀 To start the portal in production:"
    echo "   ./start-production.sh"
    echo ""
    echo "🌐 Portal will be available at:"
    echo "   http://fishing.thepeaveys.net"
    echo "   http://$(hostname -I | awk '{print $1}' | head -n1):5000"
    echo ""
    echo "📊 Database features:"
    echo "   - Automatic weather data storage"
    echo "   - Historical data access"
    echo "   - Fishing conditions tracking"
    echo "   - Statistics and analytics"
    echo ""
    echo "🔒 Production mode:"
    echo "   - Debug mode: Disabled"
    echo "   - Threading: Enabled"
    echo "   - Security: Enhanced"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Configure web server (Apache/Nginx) to proxy to port 5000"
    echo "   2. Set up systemd service (optional): see PRODUCTION_DEPLOYMENT.md"
    echo "   3. Configure SSL certificate (recommended)"
    echo ""
    echo "🎣 Happy fishing!"
else
    echo ""
    echo "❌ Deployment test failed. Please check the errors above."
    exit 1
fi
