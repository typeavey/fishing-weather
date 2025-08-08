#!/bin/bash

# Setup systemd service for Fishing Weather Portal on Rocky Linux
# Run this script on your Rocky Linux server

echo "🔧 Setting up systemd service for Fishing Weather Portal..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the fishing-weather directory."
    exit 1
fi

# Create the systemd service file
echo "📝 Creating systemd service file..."
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
ExecStart=/home/typeavey/fishing-weather/venv/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd daemon
echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable the service
echo "✅ Enabling fishing-weather service..."
sudo systemctl enable fishing-weather

# Start the service
echo "🚀 Starting fishing-weather service..."
sudo systemctl start fishing-weather

# Check status
echo "📊 Checking service status..."
sleep 3
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

echo ""
echo "🎉 Systemd service setup complete!"
echo ""
echo "📋 Useful commands:"
echo "   Check status: sudo systemctl status fishing-weather"
echo "   Start service: sudo systemctl start fishing-weather"
echo "   Stop service: sudo systemctl stop fishing-weather"
echo "   Restart service: sudo systemctl restart fishing-weather"
echo "   View logs: sudo journalctl -u fishing-weather -f"
echo ""
echo "🌐 Your portal should be available at:"
echo "   http://fishing.thepeaveys.net"
echo "   http://localhost:5000"
