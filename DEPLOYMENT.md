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
