#!/bin/bash

# Production Deployment Script for Fishing Weather Portal
# Designed for Rocky Linux server environment

set -e  # Exit on any error

echo "🚀 Deploying Fishing Weather Portal to Production..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the fishing-weather directory."
    exit 1
fi

# Check if running as correct user
if [ "$USER" != "typeavey" ]; then
    echo "⚠️  Warning: Running as $USER, expected typeavey"
fi

# Step 1: Stop existing services
echo "🛑 Stopping existing services..."
sudo systemctl stop fishing-weather 2>/dev/null || true
pkill -f "python.*app.py" 2>/dev/null || true

# Step 2: Update from git (if in git repository)
if [ -d ".git" ]; then
    echo "📥 Updating from git repository..."
    git pull origin main 2>/dev/null || echo "⚠️  Git pull failed or not needed"
fi

# Step 3: Set up Python environment
echo "🐍 Setting up Python environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 4: Initialize database
echo "🗄️  Initializing database..."
if [ ! -f "weather_data.db" ]; then
    python3 working_database.py
fi

# Step 5: Test the application
echo "🧪 Testing application..."
python3 -c "
from app import app, db
print('✅ Flask app imported successfully')
print('✅ Database connected successfully')
"

# Step 6: Create/update systemd service
echo "📝 Creating systemd service..."
sudo tee /etc/systemd/system/fishing-weather.service << EOF
[Unit]
Description=Fishing Weather Portal (Production)
After=network.target

[Service]
Type=simple
User=typeavey
Group=typeavey
WorkingDirectory=/home/typeavey/fishing-weather
Environment=PATH=/home/typeavey/fishing-weather/venv/bin
Environment=FLASK_ENV=production
Environment=FLASK_DEBUG=False
ExecStart=/home/typeavey/fishing-weather/venv/bin/python3 app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Step 7: Set proper permissions
echo "🔐 Setting permissions..."
sudo chown -R typeavey:typeavey /home/typeavey/fishing-weather
chmod +x *.sh

# Step 8: Enable and start services
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable fishing-weather
sudo systemctl start fishing-weather

# Step 9: Wait for service to start
echo "⏳ Waiting for service to start..."
sleep 5

# Step 10: Test the deployment
echo "🧪 Testing deployment..."
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ Internal service is responding"
else
    echo "❌ Internal service is not responding"
    sudo systemctl status fishing-weather --no-pager -l
    exit 1
fi

# Step 11: Test production URL
echo "🌐 Testing production URL..."
if curl -s -k https://fishing.thepeaveys.net/api/health > /dev/null; then
    echo "✅ Production portal is responding"
else
    echo "⚠️  Production portal may not be ready yet"
fi

# Step 12: Create backup
echo "💾 Creating backup..."
./backup-database.sh

echo ""
echo "🎉 Production deployment complete!"
echo ""
echo "📊 Service Status:"
sudo systemctl status fishing-weather --no-pager -l | head -10
echo ""
echo "🌐 Your portal is available at:"
echo "   https://fishing.thepeaveys.net"
echo ""
echo "📋 Useful commands:"
echo "   sudo systemctl status fishing-weather    # Check service status"
echo "   sudo systemctl restart fishing-weather   # Restart service"
echo "   sudo journalctl -u fishing-weather -f   # View logs"
echo "   ./backup-database.sh                    # Backup database"
echo ""
echo "🔄 To update in the future, simply run:"
echo "   ./deploy-production.sh"
