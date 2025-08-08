# 🌐 Web Server Configuration - Rocky Linux

## 🎯 **Your Setup**

- **Code Directory**: `/home/typeavey/fishing-weather`
- **Web Directory**: `/var/www/fishing.thepeaveys.net/public_html`
- **Domain**: `fishing.thepeaveys.net`
- **Port**: 5000 (Flask app)

## 🚀 **Deployment Steps**

### **Step 1: Deploy the Application**
```bash
# Navigate to your code directory
cd /home/typeavey/fishing-weather

# Deploy the application
./deploy-production.sh
```

This will:
- ✅ Set up Python virtual environment
- ✅ Install dependencies
- ✅ Initialize SQLite database
- ✅ Copy static files to `/var/www/fishing.thepeaveys.net/public_html`
- ✅ Create symbolic links for easy updates

### **Step 2: Configure Web Server**

#### **Option A: Apache (Recommended)**

1. **Install Apache and mod_proxy**:
```bash
sudo dnf install -y httpd mod_ssl
sudo systemctl enable httpd
sudo systemctl start httpd
```

2. **Create Apache Virtual Host**:
```bash
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
```

3. **Enable required modules**:
```bash
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo systemctl restart httpd
```

#### **Option B: Nginx**

1. **Install Nginx**:
```bash
sudo dnf install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

2. **Create Nginx Configuration**:
```bash
sudo tee /etc/nginx/conf.d/fishing.thepeaveys.net.conf << 'EOF'
server {
    listen 80;
    server_name fishing.thepeaveys.net www.fishing.thepeaveys.net;
    root /var/www/fishing.thepeaveys.net/public_html;
    index index.html;

    # Proxy API requests to Flask app
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Serve static files
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Logs
    access_log /var/log/nginx/fishing.thepeaveys.net.access.log;
    error_log /var/log/nginx/fishing.thepeaveys.net.error.log;
}
EOF
```

3. **Test and restart Nginx**:
```bash
sudo nginx -t
sudo systemctl restart nginx
```

### **Step 3: Configure Firewall**
```bash
# Allow HTTP and HTTPS
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### **Step 4: Start the Flask Application**

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

## 🔧 **Configuration Details**

### **Directory Structure**
```
/home/typeavey/fishing-weather/          # Code directory
├── app.py                              # Flask application
├── working_database.py                 # Database module
├── weather_data.db                     # SQLite database
├── venv/                               # Python virtual environment
├── fishing-website/                    # Static files
│   ├── index.html
│   ├── weather.html
│   ├── locations.html
│   ├── forecast.html
│   └── js/
└── ...

/var/www/fishing.thepeaveys.net/public_html/  # Web directory
├── index.html                              # Copied from fishing-website
├── weather.html
├── locations.html
├── forecast.html
├── js/
└── fishing-website -> /home/typeavey/fishing-weather/fishing-website  # Symlink
```

### **URL Structure**
- **Main Portal**: `http://fishing.thepeaveys.net/`
- **Weather Page**: `http://fishing.thepeaveys.net/weather.html`
- **Locations Page**: `http://fishing.thepeaveys.net/locations.html`
- **Forecast Page**: `http://fishing.thepeaveys.net/forecast.html`
- **API Endpoints**: `http://fishing.thepeaveys.net/api/weather`, etc.

## 🔒 **SSL/HTTPS Configuration (Recommended)**

### **Using Let's Encrypt**
```bash
# Install certbot
sudo dnf install -y certbot python3-certbot-apache  # For Apache
# OR
sudo dnf install -y certbot python3-certbot-nginx   # For Nginx

# Get SSL certificate
sudo certbot --apache -d fishing.thepeaveys.net  # For Apache
# OR
sudo certbot --nginx -d fishing.thepeaveys.net   # For Nginx

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 **Monitoring and Maintenance**

### **Check Application Status**
```bash
# Check Flask app
sudo systemctl status fishing-weather

# Check web server
sudo systemctl status httpd  # or nginx

# Check logs
sudo journalctl -u fishing-weather -f
sudo tail -f /var/log/httpd/fishing.thepeaveys.net-error.log  # Apache
# OR
sudo tail -f /var/log/nginx/fishing.thepeaveys.net.error.log  # Nginx
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
sudo chown -R $USER:$USER /var/www/fishing.thepeaveys.net/public_html
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
   # Check web server status
   sudo systemctl status httpd  # or nginx
   
   # Check configuration
   sudo apachectl configtest  # Apache
   # OR
   sudo nginx -t              # Nginx
   ```

4. **API Endpoints Not Working**
   ```bash
   # Test API directly
   curl http://localhost:5000/api/health
   
   # Check proxy configuration
   sudo grep -r "ProxyPass" /etc/httpd/conf.d/  # Apache
   # OR
   sudo grep -r "proxy_pass" /etc/nginx/conf.d/ # Nginx
   ```

## 🎉 **Success Checklist**

- ✅ **Code deployed** to `/home/typeavey/fishing-weather`
- ✅ **Static files copied** to `/var/www/fishing.thepeaveys.net/public_html`
- ✅ **Web server configured** (Apache/Nginx)
- ✅ **Flask app running** on port 5000
- ✅ **Systemd service** configured (optional)
- ✅ **Firewall configured** for HTTP/HTTPS
- ✅ **SSL certificate** installed (recommended)
- ✅ **Domain accessible** at `http://fishing.thepeaveys.net`

## 🎣 **Your Portal is Ready!**

Your fishing weather portal is now **fully configured** for production use with:
- **Domain**: `http://fishing.thepeaveys.net`
- **Database**: SQLite with automatic storage
- **API**: RESTful endpoints for data access
- **Security**: SSL/HTTPS ready
- **Monitoring**: Comprehensive logging
- **Backup**: Automated database backups

**🎣 Happy fishing with your production-ready weather portal!**
