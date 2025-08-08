# 🎣 Fishing Weather Portal

A modern, interactive fishing weather portal with real-time weather data, historical analysis, SQLite database integration, and SSL/HTTPS support.

## 🚀 Quick Start

### Local Development
```bash
# Clone the repository
git clone <your-repo-url>
cd fishing-weather

# Deploy locally
./deploy.sh

# Start the portal
./start-portal.sh
```

### Production Deployment (Rocky Linux with SSL/HTTPS)
```bash
# Clone to production server
git clone <your-repo-url> /home/typeavey/fishing-weather
cd /home/typeavey/fishing-weather

# Check SSL configuration (if you have existing SSL)
./check-ssl-config.sh

# Deploy to production with SSL support
./setup-production.sh
```

## 🌐 Access the Portal

### Local Development
- **Main Portal**: http://localhost:5000
- **Weather Page**: http://localhost:5000/weather.html
- **Locations Page**: http://localhost:5000/locations.html
- **Forecast Page**: http://localhost:5000/forecast.html

### Production (with SSL/HTTPS)
- **Main Portal**: https://fishing.thepeaveys.net
- **Weather Page**: https://fishing.thepeaveys.net/weather.html
- **Locations Page**: https://fishing.thepeaveys.net/locations.html
- **Forecast Page**: https://fishing.thepeaveys.net/forecast.html

## 🗄️ Database Features

### SQLite Integration
- **Automatic Storage**: Weather data automatically stored when fetched
- **Historical Data**: Access to past weather conditions
- **Fishing Analysis**: Enhanced fishing condition tracking
- **Statistics**: Real-time database statistics and analytics

### New API Endpoints
- **Historical Data**: `GET /api/weather/history?location=Winnipesaukee&days=30`
- **Statistics**: `GET /api/weather/statistics`
- **Fishing Conditions**: `GET /api/fishing/conditions?location=Winnipesaukee&days=30`
- **Health Check**: `GET /api/health` (includes database status)

## 🔒 SSL/HTTPS Support

### Production SSL Configuration
The portal is configured to work with your existing SSL setup:

- **Automatic HTTPS redirect**: All HTTP traffic is redirected to HTTPS
- **Security headers**: HSTS, X-Content-Type-Options, X-Frame-Options, X-XSS-Protection
- **SSL certificate support**: Works with Let's Encrypt, self-signed, or commercial certificates

### SSL Certificate Locations
The setup script looks for SSL certificates in these common locations:
- **Certificate**: `/etc/ssl/certs/fishing.thepeaveys.net.crt` or `/etc/letsencrypt/live/fishing.thepeaveys.net/cert.pem`
- **Private Key**: `/etc/ssl/private/fishing.thepeaveys.net.key` or `/etc/letsencrypt/live/fishing.thepeaveys.net/privkey.pem`
- **Chain Certificate**: `/etc/ssl/certs/fishing.thepeaveys.net.chain.crt` (optional)

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
- `./deploy.sh` - Local deployment
- `./setup-production.sh` - Production deployment with SSL
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
- **Total Records**: 57 weather records
- **Locations**: 7 fishing locations (Champlain, First Connecticut, Mascoma, Newfound, Squam, Sunapee, Winnipesaukee)
- **Date Range**: August 8-15, 2025
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
./setup-production.sh

# 3. Verify deployment
curl -k https://fishing.thepeaveys.net/api/health
```

## 🔄 Updates and Maintenance

### Automated Updates
```bash
# Update the portal
./update-deployment.sh
```

### Manual Updates
```bash
# Pull latest changes
git pull origin main

# Restart services
sudo systemctl restart fishing-weather httpd
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
