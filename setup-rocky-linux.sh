#!/bin/bash

# Fishing Weather Portal - Rocky Linux Setup Script
# Specifically configured for:
# - Code: /home/typeavey/fishing-weather
# - Web: /var/www/fishing.thepeaveys.net/public_html
# - Domain: fishing.thepeaveys.net

echo "🎣 Setting up Fishing Weather Portal for Rocky Linux..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the fishing-weather directory."
    exit 1
fi

# Check if running as correct user
if [ "$USER" != "typeavey" ]; then
    echo "⚠️  Warning: This script is designed to run as user 'typeavey'"
    echo "   Current user: $USER"
    read -p "   Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
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
    echo "🎉 Rocky Linux setup successful!"
    echo ""
    echo "📁 Directory Structure:"
    echo "   Code: $(pwd)"
    echo "   Web: $WEB_DIR"
    echo "   Database: $(pwd)/weather_data.db"
    echo ""
    echo "🚀 Next Steps:"
    echo ""
    echo "1. Configure web server (Apache/Nginx):"
    echo "   - See WEB_SERVER_CONFIG.md for detailed instructions"
    echo "   - Or run: sudo dnf install -y httpd mod_ssl"
    echo ""
    echo "2. Start the Flask application:"
    echo "   ./start-production.sh"
    echo ""
    echo "3. Set up systemd service (recommended):"
    echo "   sudo tee /etc/systemd/system/fishing-weather.service << 'EOF'"
    echo "   [Unit]"
    echo "   Description=Fishing Weather Portal"
    echo "   After=network.target"
    echo ""
    echo "   [Service]"
    echo "   Type=simple"
    echo "   User=typeavey"
    echo "   Group=typeavey"
    echo "   WorkingDirectory=$(pwd)"
    echo "   Environment=PATH=$(pwd)/venv/bin"
    echo "   ExecStart=$(pwd)/venv/bin/python3 app.py"
    echo "   Restart=always"
    echo "   RestartSec=10"
    echo ""
    echo "   [Install]"
    echo "   WantedBy=multi-user.target"
    echo "   EOF"
    echo ""
    echo "4. Enable and start service:"
    echo "   sudo systemctl daemon-reload"
    echo "   sudo systemctl enable fishing-weather"
    echo "   sudo systemctl start fishing-weather"
    echo ""
    echo "🌐 Your portal will be available at:"
    echo "   http://fishing.thepeaveys.net"
    echo "   http://$(hostname -I | awk '{print $1}' | head -n1):5000"
    echo ""
    echo "📊 Database features:"
    echo "   - Automatic weather data storage"
    echo "   - Historical data access"
    echo "   - Fishing conditions tracking"
    echo "   - Statistics and analytics"
    echo ""
    echo "🎣 Happy fishing!"
else
    echo ""
    echo "❌ Setup test failed. Please check the errors above."
    exit 1
fi
