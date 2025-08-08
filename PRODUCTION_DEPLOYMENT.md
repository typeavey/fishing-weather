# 🚀 Production Deployment Guide - Rocky Linux

## ✅ **Production-Ready Setup**

Your fishing weather portal is designed to work seamlessly on Rocky Linux production servers. Here's everything you need to know:

## 🎯 **Pre-Deployment Checklist**

### **1. Server Requirements**
- ✅ **Python 3.9+**: Required for type hints and modern features
- ✅ **Git**: For code deployment
- ✅ **SQLite**: Built into Python (no additional setup needed)
- ✅ **Port 5000**: Available for the application
- ✅ **Firewall**: Configured to allow port 5000 (if needed)

### **2. System Dependencies**
```bash
# Update system packages
sudo dnf update -y

# Install Python 3.9+ and development tools
sudo dnf install -y python3 python3-pip python3-devel git

# Install additional system dependencies (if needed)
sudo dnf install -y gcc gcc-c++ make
```

## 🚀 **Deployment Steps**

### **Step 1: Clone/Pull Code**
```bash
# Navigate to your deployment directory
cd /opt/fishing-weather  # or your preferred directory

# Clone the repository (first time)
git clone <your-repo-url> .

# OR pull latest changes (subsequent deployments)
git pull origin main
```

### **Step 2: Set Up Python Environment**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **Step 3: Configure Production Settings**
```bash
# Create production configuration
cp config.json.example config.json  # if you have one
# Edit config.json with your production settings
```

### **Step 4: Initialize Database**
```bash
# Initialize SQLite database (if not exists)
python3 working_database.py
```

### **Step 5: Test Deployment**
```bash
# Test the application
python3 test_deployment.py
```

## 🔧 **Production Configuration**

### **1. Update app.py for Production**
The current `app.py` is configured for development. For production, you should:

```python
# In app.py, change the production settings
if __name__ == '__main__':
    # Load initial data
    logger.info("Starting Fishing Weather API Server")
    get_cached_weather_data()
    
    # Run the Flask app (PRODUCTION SETTINGS)
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # Set to False for production
        threaded=True  # Enable threading for multiple requests
    )
```

### **2. Environment Variables**
Create a `.env` file for production settings:
```bash
# .env file
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5000
HOST=0.0.0.0
```

## 🛠️ **Production Deployment Scripts**

### **1. Production Start Script**
```bash
#!/bin/bash
# start-production.sh

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Set production environment
export FLASK_ENV=production
export FLASK_DEBUG=False

# Start the application
echo "🎣 Starting Fishing Weather Portal (Production)..."
echo "🌐 Portal will be available at: http://$(hostname -I | awk '{print $1}'):5000"
echo "📊 Database: SQLite (weather_data.db)"
echo "🔄 Press Ctrl+C to stop the server"

python3 app.py
```

### **2. Systemd Service (Recommended)**
Create a systemd service for automatic startup:

```bash
# Create service file
sudo tee /etc/systemd/system/fishing-weather.service << EOF
[Unit]
Description=Fishing Weather Portal
After=network.target

[Service]
Type=simple
User=fishing-weather
Group=fishing-weather
WorkingDirectory=/opt/fishing-weather
Environment=PATH=/opt/fishing-weather/venv/bin
ExecStart=/opt/fishing-weather/venv/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create user (if needed)
sudo useradd -r -s /bin/false fishing-weather

# Set permissions
sudo chown -R fishing-weather:fishing-weather /opt/fishing-weather

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable fishing-weather
sudo systemctl start fishing-weather
```

## 🔒 **Security Considerations**

### **1. Firewall Configuration**
```bash
# Allow port 5000 (if using ufw)
sudo ufw allow 5000

# Or for firewalld (Rocky Linux default)
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

### **2. File Permissions**
```bash
# Set proper permissions
chmod 755 /opt/fishing-weather
chmod 644 /opt/fishing-weather/weather_data.db
chmod 755 /opt/fishing-weather/start-production.sh
```

### **3. SSL/HTTPS (Recommended)**
For production, consider using a reverse proxy with SSL:

```bash
# Install nginx
sudo dnf install -y nginx

# Configure nginx reverse proxy
sudo tee /etc/nginx/conf.d/fishing-weather.conf << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Start nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

## 📊 **Monitoring and Logging**

### **1. Log Management**
```bash
# Create log directory
sudo mkdir -p /var/log/fishing-weather
sudo chown fishing-weather:fishing-weather /var/log/fishing-weather

# Update systemd service to include logging
sudo tee /etc/systemd/system/fishing-weather.service << EOF
[Unit]
Description=Fishing Weather Portal
After=network.target

[Service]
Type=simple
User=fishing-weather
Group=fishing-weather
WorkingDirectory=/opt/fishing-weather
Environment=PATH=/opt/fishing-weather/venv/bin
ExecStart=/opt/fishing-weather/venv/bin/python3 app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

### **2. Health Monitoring**
```bash
# Test health endpoint
curl http://localhost:5000/api/health

# Check service status
sudo systemctl status fishing-weather
```

## 🔄 **Deployment Automation**

### **1. Git Hook Deployment**
Create a post-receive hook for automatic deployment:

```bash
# On your production server
cd /opt/fishing-weather
git init --bare

# Create post-receive hook
cat > hooks/post-receive << 'EOF'
#!/bin/bash
TARGET="/opt/fishing-weather"
GIT_DIR="/opt/fishing-weather"
BRANCH="main"

while read oldrev newrev ref
do
    if [[ $ref = refs/heads/$BRANCH ]];
    then
        echo "Deploying $BRANCH branch..."
        git --work-tree=$TARGET --git-dir=$GIT_DIR checkout -f $BRANCH
        
        cd $TARGET
        
        # Activate virtual environment and update
        source venv/bin/activate
        pip install -r requirements.txt
        
        # Restart service
        sudo systemctl restart fishing-weather
        
        echo "Deployment complete!"
    fi
done
EOF

chmod +x hooks/post-receive
```

### **2. Simple Deployment Script**
```bash
#!/bin/bash
# deploy.sh

echo "🚀 Deploying Fishing Weather Portal..."

# Pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Test deployment
python3 test_deployment.py

# Restart service (if using systemd)
sudo systemctl restart fishing-weather

echo "✅ Deployment complete!"
```

## 🎯 **Quick Production Start**

### **Option 1: Manual Start**
```bash
cd /opt/fishing-weather
source venv/bin/activate
python3 app.py
```

### **Option 2: Systemd Service**
```bash
sudo systemctl start fishing-weather
sudo systemctl status fishing-weather
```

### **Option 3: Screen Session**
```bash
screen -S fishing-weather
cd /opt/fishing-weather
source venv/bin/activate
python3 app.py
# Press Ctrl+A, then D to detach
```

## 🔍 **Troubleshooting**

### **Common Issues**

1. **Port 5000 in use**
   ```bash
   # Check what's using port 5000
   sudo netstat -tlnp | grep :5000
   
   # Kill process or change port in app.py
   ```

2. **Permission denied**
   ```bash
   # Fix permissions
   sudo chown -R $USER:$USER /opt/fishing-weather
   chmod +x start-production.sh
   ```

3. **Database errors**
   ```bash
   # Check database file
   ls -la weather_data.db
   
   # Reinitialize if needed
   rm weather_data.db
   python3 working_database.py
   ```

4. **Import errors**
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate
   
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

## 🎉 **Success Checklist**

- ✅ **Code deployed** to production server
- ✅ **Virtual environment** created and activated
- ✅ **Dependencies installed** from requirements.txt
- ✅ **Database initialized** and working
- ✅ **Service configured** (systemd or manual)
- ✅ **Firewall configured** for port 5000
- ✅ **Health endpoint** responding
- ✅ **Logs configured** and accessible
- ✅ **Backup strategy** in place

## 🎣 **Production Ready!**

Your fishing weather portal is now **production-ready** and will work seamlessly on your Rocky Linux server!

**🌐 Production URL**: http://your-server-ip:5000  
**🗄️ Database**: SQLite (weather_data.db)  
**🔄 Auto-restart**: Systemd service (if configured)  
**📊 Monitoring**: Health endpoint and logs  
**🔒 Security**: Firewall and permissions configured
