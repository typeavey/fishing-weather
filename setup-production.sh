#!/bin/bash

# Production Setup for Fishing Weather Portal on Rocky Linux
# This script sets up the proper production environment

echo "🏭 Setting up Fishing Weather Portal for Production..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the fishing-weather directory."
    exit 1
fi

# Step 1: Stop any existing processes
echo "🛑 Stopping any existing processes..."
pkill -f "python.*app.py" 2>/dev/null || true
sudo systemctl stop fishing-weather 2>/dev/null || true

# Step 2: Create systemd service for internal Flask app (port 5000)
echo "📝 Creating systemd service for internal Flask app..."
sudo tee /etc/systemd/system/fishing-weather.service << EOF
[Unit]
Description=Fishing Weather Portal (Internal)
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

[Install]
WantedBy=multi-user.target
EOF

# Step 3: Set up Apache virtual host for production
echo "🌐 Setting up Apache virtual host..."
sudo tee /etc/httpd/conf.d/fishing-weather.conf << EOF
# Fishing Weather Portal Production Configuration
<VirtualHost *:80>
    ServerName fishing.thepeaveys.net
    ServerAlias www.fishing.thepeaveys.net
    
    # Proxy all requests to internal Flask app
    ProxyPreserveHost On
    ProxyPass / http://localhost:5000/
    ProxyPassReverse / http://localhost:5000/
    
    # Logging
    ErrorLog /var/log/httpd/fishing-weather-error.log
    CustomLog /var/log/httpd/fishing-weather-access.log combined
    
    # Security headers
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options DENY
    Header always set X-XSS-Protection "1; mode=block"
</VirtualHost>
EOF

# Step 4: Enable required Apache modules
echo "🔧 Enabling Apache modules..."
sudo dnf install -y mod_proxy mod_proxy_http mod_headers 2>/dev/null || true

# Step 5: Configure firewall
echo "🔥 Configuring firewall..."
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# Step 6: Set proper permissions
echo "🔐 Setting permissions..."
sudo chown -R typeavey:typeavey /home/typeavey/fishing-weather
chmod 755 /home/typeavey/fishing-weather
chmod 644 /home/typeavey/fishing-weather/weather_data.db

# Step 7: Start services
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable fishing-weather
sudo systemctl start fishing-weather

# Step 8: Restart Apache
echo "🔄 Restarting Apache..."
sudo systemctl restart httpd

# Step 9: Check status
echo "📊 Checking service status..."
sleep 5
if sudo systemctl is-active --quiet fishing-weather; then
    echo "✅ Internal Flask service started successfully!"
else
    echo "❌ Internal Flask service failed to start"
    sudo systemctl status fishing-weather --no-pager -l
    exit 1
fi

if sudo systemctl is-active --quiet httpd; then
    echo "✅ Apache service is running!"
else
    echo "❌ Apache service failed to start"
    sudo systemctl status httpd --no-pager -l
    exit 1
fi

# Step 10: Test the application
echo "🧪 Testing application..."
sleep 3
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ Internal Flask app is responding"
else
    echo "⚠️  Internal Flask app may not be ready"
fi

if curl -s http://fishing.thepeaveys.net/api/health > /dev/null; then
    echo "✅ Production portal is responding"
else
    echo "⚠️  Production portal may not be ready yet"
fi

echo ""
echo "🎉 Production setup complete!"
echo ""
echo "🌐 Your portal is available at:"
echo "   http://fishing.thepeaveys.net"
echo "   http://www.fishing.thepeaveys.net"
echo ""
echo "📋 Useful commands:"
echo "   Check Flask service: sudo systemctl status fishing-weather"
echo "   Check Apache service: sudo systemctl status httpd"
echo "   View Flask logs: sudo journalctl -u fishing-weather -f"
echo "   View Apache logs: sudo tail -f /var/log/httpd/fishing-weather-access.log"
echo ""
echo "🔧 Management:"
echo "   Restart Flask: sudo systemctl restart fishing-weather"
echo "   Restart Apache: sudo systemctl restart httpd"
echo "   Full restart: sudo systemctl restart fishing-weather httpd"
