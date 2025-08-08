# 🚀 Rocky Linux Quick Start Guide

## 🎯 **Your Specific Setup**

- **Code Directory**: `/home/typeavey/fishing-weather`
- **Web Directory**: `/var/www/fishing.thepeaveys.net/public_html`
- **Domain**: `fishing.thepeaveys.net`
- **User**: `typeavey`

## 🚀 **Quick Deployment**

### **Step 1: Deploy to Production**
```bash
# Navigate to your code directory
cd /home/typeavey/fishing-weather

# Run the Rocky Linux setup script
./setup-rocky-linux.sh
```

This will:
- ✅ Set up Python virtual environment
- ✅ Install dependencies
- ✅ Initialize SQLite database
- ✅ Copy static files to web directory
- ✅ Create symbolic links
- ✅ Test the deployment

### **Step 2: Configure Web Server (Apache)**

```bash
# Install Apache and required modules
sudo dnf install -y httpd mod_ssl

# Create virtual host configuration
sudo tee /etc/httpd/conf.d/fishing.thepeaveys.net.conf << 'EOF'
<VirtualHost *:80>
    ServerName fishing.thepeaveys.net
    ServerAlias www.fishing.thepeaveys.net
    DocumentRoot /var/www/fishing.thepeaveys.net/public_html
    
    # Proxy Flask app to port 5000
    ProxyPreserveHost On
    ProxyPass /api/ http://127.0.0.1:5000/api/
    ProxyPassReverse /api/ http://127.0.0.1:5000/api/
    
    # Serve static files directly
    <Directory /var/www/fishing.thepeaveys.net/public_html>
        AllowOverride All
        Require all granted
    </Directory>
    
    # Logs
    ErrorLog logs/fishing.thepeaveys.net-error.log
    CustomLog logs/fishing.thepeaveys.net-access.log combined
</VirtualHost>
EOF

# Enable required modules and start Apache
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo systemctl enable httpd
sudo systemctl start httpd
```

### **Step 3: Start the Application**

#### **Option A: Manual Start**
```bash
cd /home/typeavey/fishing-weather
./start-production.sh
```

#### **Option B: Systemd Service (Recommended)**
```bash
# Create systemd service
sudo tee /etc/systemd/system/fishing-weather.service << 'EOF'
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
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable fishing-weather
sudo systemctl start fishing-weather
```

### **Step 4: Configure Firewall**
```bash
# Allow HTTP and HTTPS
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 🌐 **Access Your Portal**

- **Main Portal**: `http://fishing.thepeaveys.net/`
- **Weather Page**: `http://fishing.thepeaveys.net/weather.html`
- **Locations Page**: `http://fishing.thepeaveys.net/locations.html`
- **Forecast Page**: `http://fishing.thepeaveys.net/forecast.html`
- **API Health**: `http://fishing.thepeaveys.net/api/health`

## 🔧 **Management Commands**

### **Check Status**
```bash
# Check Flask app
sudo systemctl status fishing-weather

# Check web server
sudo systemctl status httpd

# Check logs
sudo journalctl -u fishing-weather -f
```

### **Update Application**
```bash
# Pull latest changes
cd /home/typeavey/fishing-weather
git pull origin main

# Reinstall dependencies (if needed)
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart fishing-weather

# Update static files
sudo cp -r fishing-website/* /var/www/fishing.thepeaveys.net/public_html/
sudo chown -R typeavey:typeavey /var/www/fishing.thepeaveys.net/public_html
```

### **Backup Database**
```bash
cd /home/typeavey/fishing-weather
./backup-database.sh
```

## 🎯 **Troubleshooting**

### **Common Issues**

1. **Permission Denied**
   ```bash
   sudo chown -R typeavey:typeavey /var/www/fishing.thepeaveys.net/public_html
   sudo chmod -R 755 /var/www/fishing.thepeaveys.net/public_html
   ```

2. **Port 5000 Not Accessible**
   ```bash
   # Check if Flask app is running
   sudo systemctl status fishing-weather
   
   # Check if port is listening
   sudo netstat -tlnp | grep :5000
   ```

3. **Web Server Not Serving**
   ```bash
   # Check Apache status
   sudo systemctl status httpd
   
   # Check configuration
   sudo apachectl configtest
   ```

4. **API Endpoints Not Working**
   ```bash
   # Test API directly
   curl http://localhost:5000/api/health
   
   # Check proxy configuration
   sudo grep -r "ProxyPass" /etc/httpd/conf.d/
   ```

## 🎉 **Success Checklist**

- ✅ **Code deployed** to `/home/typeavey/fishing-weather`
- ✅ **Static files copied** to `/var/www/fishing.thepeaveys.net/public_html`
- ✅ **Apache configured** with proxy to port 5000
- ✅ **Flask app running** on port 5000
- ✅ **Systemd service** configured and running
- ✅ **Firewall configured** for HTTP/HTTPS
- ✅ **Domain accessible** at `http://fishing.thepeaveys.net`

## 🎣 **Your Portal is Ready!**

Your fishing weather portal is now **fully operational** at:
**http://fishing.thepeaveys.net**

**Features:**
- 🌤️ Real-time weather data
- 📊 Historical data storage
- 🎣 Fishing condition analysis
- 📱 Mobile responsive design
- 🔄 Automatic data updates
- 🗄️ SQLite database integration

**🎣 Happy fishing with your production-ready weather portal!**
