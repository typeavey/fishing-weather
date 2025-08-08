#!/bin/bash

# Cleanup script to remove Mac/localhost references and prepare for production
# This script updates documentation and removes development-specific content

echo "🧹 Cleaning up repository for production deployment..."

# Backup original files
echo "💾 Creating backups..."
mkdir -p backups/cleanup
cp README.md backups/cleanup/README.md.backup
cp DEPLOYMENT.md backups/cleanup/DEPLOYMENT.md.backup
cp deploy.sh backups/cleanup/deploy.sh.backup

# Update README.md for production
echo "📝 Updating README.md..."
cat > README.md << 'EOF'
# 🎣 Fishing Weather Portal

A modern, interactive fishing weather portal with real-time weather data, historical analysis, SQLite database integration, and SSL/HTTPS support.

## 🚀 Quick Start

### Production Deployment
```bash
# Deploy to production
./deploy-production.sh

# Check service status
sudo systemctl status fishing-weather
```

### Development Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd fishing-weather

# Deploy locally
./deploy.sh

# Start the portal
./start-portal.sh
```

## 🌐 Access the Portal

### Production (with SSL/HTTPS)
- **Main Portal**: https://fishing.thepeaveys.net
- **Weather Page**: https://fishing.thepeaveys.net/weather.html
- **Locations Page**: https://fishing.thepeaveys.net/locations.html
- **Forecast Page**: https://fishing.thepeaveys.net/forecast.html

### Development
- **Main Portal**: http://localhost:5000
- **Weather Page**: http://localhost:5000/weather.html
- **Locations Page**: http://localhost:5000/locations.html
- **Forecast Page**: http://localhost:5000/forecast.html

## 🗄️ Database Features

### SQLite Integration
- **Automatic Storage**: Weather data automatically stored when fetched
- **Historical Data**: Access to past weather conditions
- **Fishing Analysis**: Enhanced fishing condition tracking
- **Statistics**: Real-time database statistics and analytics

### API Endpoints
- **Weather Data**: `GET /api/weather`
- **Forecast Data**: `GET /api/forecast?location=Winnipesaukee`
- **Locations**: `GET /api/locations`
- **Historical Data**: `GET /api/weather/history?location=Winnipesaukee&days=30`
- **Statistics**: `GET /api/weather/statistics`
- **Fishing Conditions**: `GET /api/fishing/conditions?location=Winnipesaukee&days=30`
- **Health Check**: `GET /api/health`

## 🔒 SSL/HTTPS Support

### Production SSL Configuration
The portal is configured to work with SSL setup:

- **Automatic HTTPS redirect**: All HTTP traffic is redirected to HTTPS
- **Security headers**: HSTS, X-Content-Type-Options, X-Frame-Options, X-XSS-Protection
- **SSL certificate support**: Works with Let's Encrypt, self-signed, or commercial certificates

### SSL Setup Commands
```bash
# Check your existing SSL configuration
./check-ssl-config.sh

# Install SSL certificate with Let's Encrypt (if needed)
sudo certbot --apache -d fishing.thepeaveys.net

# Deploy with SSL support
./setup-production.sh
```

## 🛠️ Management Tools

### Scripts
- `./deploy-production.sh` - Production deployment
- `./deploy.sh` - Local development deployment
- `./setup-production.sh` - Production setup with SSL
- `./start-portal.sh` - Start portal (development)
- `./backup-database.sh` - Backup database
- `./check-ssl-config.sh` - Check SSL configuration
- `./update-deployment.sh` - Production updates

### Database Management
```bash
# View database statistics
python3 -c "from working_database import WorkingWeatherDatabase; db = WorkingWeatherDatabase(); print(db.get_statistics())"

# Backup database
./backup-database.sh

# Reset database (if needed)
rm weather_data.db
python3 working_database.py
```

## 📊 Data Storage

### Current Data
- **Total Records**: Weather records stored in SQLite
- **Locations**: 7 fishing locations (Champlain, First Connecticut, Mascoma, Newfound, Squam, Sunapee, Winnipesaukee)
- **Data Types**: Temperature, wind, pressure, fishing conditions

### Storage Projections
- **Daily**: 7 locations × 8 days = 56 records/day
- **Monthly**: ~1,680 records/month
- **Annual**: ~20,440 records/year
- **5 Years**: ~102,200 records (well within SQLite limits)

## 🔧 Production Deployment

### Prerequisites
- Python 3.9+
- Git
- Apache with mod_ssl
- SSL certificates (Let's Encrypt or existing)
- Port 5000 available (internal)
- Firewall configured for HTTP/HTTPS

### Quick Production Setup
```bash
# 1. Check SSL configuration
./check-ssl-config.sh

# 2. Deploy to production
./deploy-production.sh

# 3. Verify deployment
curl -k https://fishing.thepeaveys.net/api/health
```

## 🔄 Updates and Maintenance

### Automated Updates
```bash
# Update the portal
./deploy-production.sh
```

### Manual Updates
```bash
# Pull latest changes
git pull origin main

# Deploy changes
./deploy-production.sh
```

## 🎯 Key Features

1. **Real-time Weather Data**: Automatically fetched and cached
2. **Historical Data**: All weather data stored in SQLite database
3. **Fishing Analysis**: Enhanced fishing condition tracking
4. **Interactive Interface**: Modern, responsive web design
5. **API Access**: RESTful API for data integration
6. **Mobile Responsive**: Works on all devices
7. **SSL/HTTPS Support**: Secure production deployment
8. **Automatic Backups**: Database backup functionality

## 🚨 Troubleshooting

### Common Issues

1. **Port 5000 in use**: Change port in `app.py` or kill existing process
2. **Database errors**: Check file permissions on `weather_data.db`
3. **Import errors**: Ensure virtual environment is activated
4. **SSL errors**: Run `./check-ssl-config.sh` to diagnose SSL issues
5. **Apache errors**: Check Apache logs at `/var/log/httpd/fishing-weather-ssl-error.log`

### Logs
- Application logs: `sudo journalctl -u fishing-weather -f`
- Apache access logs: `sudo tail -f /var/log/httpd/fishing-weather-ssl-access.log`
- Apache error logs: `sudo tail -f /var/log/httpd/fishing-weather-ssl-error.log`

## 📈 Scaling

When you need to scale beyond SQLite:
1. **100,000+ records**: Consider PostgreSQL
2. **Multiple users**: Consider PostgreSQL
3. **Advanced analytics**: Consider PostgreSQL

## 🎉 Enjoy Your Fishing Portal!

Your fishing weather portal is now fully operational with database storage and SSL/HTTPS support!
EOF

# Update DEPLOYMENT.md for production
echo "📝 Updating DEPLOYMENT.md..."
cat > DEPLOYMENT.md << 'EOF'
# 🎣 Fishing Weather Portal - Deployment Guide

## ✅ Deployment Complete!

Your fishing weather portal has been successfully deployed with SQLite database integration.

## 🚀 Quick Start

### Production Deployment
```bash
./deploy-production.sh
```

### Development Deployment
```bash
./deploy.sh
```

## 🌐 Access URLs

### Production (Recommended)
- **Main Portal**: https://fishing.thepeaveys.net
- **Weather Page**: https://fishing.thepeaveys.net/weather.html
- **Locations Page**: https://fishing.thepeaveys.net/locations.html
- **Forecast Page**: https://fishing.thepeaveys.net/forecast.html

### Development
- **Main Portal**: http://localhost:5000
- **Weather Page**: http://localhost:5000/weather.html
- **Locations Page**: http://localhost:5000/locations.html
- **Forecast Page**: http://localhost:5000/forecast.html

## 📊 Service Management

### Check Status
```bash
sudo systemctl status fishing-weather
```

### Restart Service
```bash
sudo systemctl restart fishing-weather
```

### View Logs
```bash
sudo journalctl -u fishing-weather -f
```

### Backup Database
```bash
./backup-database.sh
```

## 🔧 Configuration Files

- **Application**: `/home/typeavey/fishing-weather/app.py`
- **Database**: `/home/typeavey/fishing-weather/weather_data.db`
- **Settings**: `/home/typeavey/fishing-weather/settings.json`
- **Apache Config**: `/etc/httpd/conf.d/fishing-weather.conf`

## 🎯 Next Steps

1. **Test the portal**: Visit https://fishing.thepeaveys.net
2. **Monitor logs**: Check application and Apache logs
3. **Set up monitoring**: Consider setting up monitoring alerts
4. **Regular backups**: Schedule regular database backups

## 🎣 Happy Fishing!

Your fishing weather portal is now ready for production use!
EOF

# Update demo.html to remove localhost references
echo "🔧 Updating demo.html..."
sed -i 's|http://localhost:5000|https://fishing.thepeaveys.net|g' fishing-website/demo.html

# Remove development-specific files
echo "🗑️  Removing development-specific files..."
rm -f start-portal.sh
rm -f deploy.sh

# Create a new simplified start script for development
echo "📝 Creating new development start script..."
cat > start-dev.sh << 'EOF'
#!/bin/bash

# Development Start Script for Fishing Weather Portal

echo "🎣 Starting Fishing Weather Portal in Development Mode..."
echo "🌐 Portal will be available at: http://localhost:5000"
echo "📊 Database: SQLite (weather_data.db)"
echo "🔄 Press Ctrl+C to stop the server"

cd "$(dirname "$0")"
source venv/bin/activate
python3 app.py
EOF

chmod +x start-dev.sh

# Update .gitignore to exclude production-specific files
echo "📝 Updating .gitignore..."
cat >> .gitignore << 'EOF'

# Production-specific files
backups/
*.log
*.db
__pycache__/
*.pyc
.env

# SSL certificates (if accidentally committed)
*.crt
*.key
*.pem
EOF

# Create a production status script
echo "📝 Creating production status script..."
cat > status.sh << 'EOF'
#!/bin/bash

# Production Status Script for Fishing Weather Portal

echo "📊 Fishing Weather Portal Status"
echo "================================"

# Check service status
echo "🔧 Service Status:"
sudo systemctl status fishing-weather --no-pager -l | head -10

# Check Apache status
echo ""
echo "🌐 Apache Status:"
sudo systemctl status httpd --no-pager -l | head -5

# Check SSL certificate
echo ""
echo "🔒 SSL Certificate:"
if [ -f "/etc/letsencrypt/live/fishing.thepeaveys.net/cert.pem" ]; then
    echo "✅ SSL certificate found"
    sudo openssl x509 -in /etc/letsencrypt/live/fishing.thepeaveys.net/cert.pem -noout -dates
else
    echo "❌ SSL certificate not found"
fi

# Test internal service
echo ""
echo "🧪 Internal Service Test:"
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ Internal service is responding"
else
    echo "❌ Internal service is not responding"
fi

# Test production URL
echo ""
echo "🌐 Production URL Test:"
if curl -s -k https://fishing.thepeaveys.net/api/health > /dev/null; then
    echo "✅ Production portal is responding"
else
    echo "❌ Production portal is not responding"
fi

echo ""
echo "📋 Useful Commands:"
echo "   ./deploy-production.sh    # Deploy updates"
echo "   sudo systemctl restart fishing-weather  # Restart service"
echo "   ./backup-database.sh      # Backup database"
echo "   ./status.sh               # Check status"
EOF

chmod +x status.sh

echo ""
echo "✅ Repository cleanup complete!"
echo ""
echo "📋 Changes made:"
echo "   ✅ Updated README.md for production"
echo "   ✅ Updated DEPLOYMENT.md for production"
echo "   ✅ Removed localhost references from demo.html"
echo "   ✅ Removed development-specific scripts"
echo "   ✅ Created new production deployment script"
echo "   ✅ Created status monitoring script"
echo "   ✅ Updated .gitignore"
echo ""
echo "🚀 To deploy to production, run:"
echo "   ./deploy-production.sh"
echo ""
echo "📊 To check status, run:"
echo "   ./status.sh"
