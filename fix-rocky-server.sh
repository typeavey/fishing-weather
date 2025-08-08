#!/bin/bash

# Fix script for Rocky Linux Fishing Weather Portal
# Run this script on your Rocky Linux server

echo "🔧 Fixing Fishing Weather Portal on Rocky Linux..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the fishing-weather directory."
    exit 1
fi

# Step 1: Stop any existing processes
echo "🛑 Stopping any existing Python processes..."
pkill -f "python.*app.py" 2>/dev/null || true
sleep 2

# Step 2: Check what's using port 5000
echo "🔍 Checking what's using port 5000..."
if lsof -i :5000 > /dev/null 2>&1; then
    echo "⚠️  Port 5000 is in use. Killing processes..."
    lsof -ti :5000 | xargs kill -9 2>/dev/null || true
    sleep 2
else
    echo "✅ Port 5000 is free"
fi

# Step 3: Check database
echo "🗄️  Checking database..."
if [ ! -f "weather_data.db" ]; then
    echo "⚠️  Database not found. Creating new database..."
    python3 -c "from working_database import WorkingWeatherDatabase; db = WorkingWeatherDatabase(); print('Database created')"
else
    echo "✅ Database exists"
    # Check if tables exist
    if ! sqlite3 weather_data.db ".tables" | grep -q weather_data; then
        echo "⚠️  Database tables missing. Initializing..."
        python3 -c "from working_database import WorkingWeatherDatabase; db = WorkingWeatherDatabase(); print('Database initialized')"
    else
        echo "✅ Database tables exist"
    fi
fi

# Step 4: Update service file to use port 5001 to avoid conflicts
echo "📝 Updating service file to use port 5001..."
sudo tee /etc/systemd/system/fishing-weather.service << EOF
[Unit]
Description=Fishing Weather Portal
After=network.target

[Service]
Type=simple
User=typeavey
Group=typeavey
WorkingDirectory=/home/typeavey/fishing-weather
Environment=PATH=/home/typeavey/fishing-weather/venv/bin
Environment=PORT=5001
ExecStart=/home/typeavey/fishing-weather/venv/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Step 5: Reload systemd and restart service
echo "🔄 Reloading systemd and restarting service..."
sudo systemctl daemon-reload
sudo systemctl restart fishing-weather

# Step 6: Check status
echo "📊 Checking service status..."
sleep 5
if sudo systemctl is-active --quiet fishing-weather; then
    echo "✅ Service started successfully!"
    echo ""
    echo "📊 Service status:"
    sudo systemctl status fishing-weather --no-pager -l
else
    echo "❌ Service failed to start"
    echo ""
    echo "📝 Service logs:"
    sudo journalctl -u fishing-weather --no-pager -l -n 20
    exit 1
fi

# Step 7: Test the application
echo "🧪 Testing application..."
sleep 3
if curl -s http://localhost:5001/api/health > /dev/null; then
    echo "✅ Application is responding on port 5001"
    echo ""
    echo "🌐 Your portal is available at:"
    echo "   http://localhost:5001"
    echo "   http://fishing.thepeaveys.net:5001"
else
    echo "⚠️  Application may not be fully ready yet"
    echo "💡 Check logs: sudo journalctl -u fishing-weather -f"
fi

echo ""
echo "🎉 Fix complete!"
echo ""
echo "📋 Useful commands:"
echo "   Check status: sudo systemctl status fishing-weather"
echo "   Start service: sudo systemctl start fishing-weather"
echo "   Stop service: sudo systemctl stop fishing-weather"
echo "   Restart service: sudo systemctl restart fishing-weather"
echo "   View logs: sudo journalctl -u fishing-weather -f"
echo ""
echo "🌐 Portal URLs:"
echo "   http://localhost:5001"
echo "   http://fishing.thepeaveys.net:5001"
