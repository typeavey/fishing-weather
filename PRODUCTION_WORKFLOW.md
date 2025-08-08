# 🎣 Fishing Weather Portal - Production Workflow Guide

## 🚀 Overview

Your fishing weather portal is now set up for **production development** with a streamlined workflow that removes Mac-specific references and focuses on your Rocky Linux server environment.

## 📁 Repository Structure

```
/home/typeavey/fishing-weather/
├── app.py                          # Main Flask application
├── fishing.py                      # Weather data processing
├── working_database.py             # Database management
├── enhanced_fishing_analysis.py    # Advanced fishing analysis
├── fishing-website/                # Static web files
│   ├── index.html
│   ├── weather.html
│   ├── locations.html
│   ├── forecast.html
│   └── js/weather-api.js
├── deploy-production.sh            # Production deployment
├── deploy-dev.sh                   # Development setup
├── git-workflow.sh                 # Git management
├── status.sh                       # Status monitoring
├── backup-database.sh              # Database backup
├── cleanup-repository.sh           # Repository cleanup
├── config.json                     # API configuration
├── settings.json                   # Location settings
├── requirements.txt                # Python dependencies
└── weather_data.db                 # SQLite database
```

## 🔄 Development Workflow

### 1. **Make Changes**
```bash
# Edit files in your repository
# All changes are tracked by git
```

### 2. **Commit Changes**
```bash
# Stage and commit your changes
./git-workflow.sh commit 'Your commit message'
```

### 3. **Deploy to Production**
```bash
# Deploy current changes to production
./deploy-production.sh
```

### 4. **Push to Git (Optional)**
```bash
# Push changes to remote repository
./git-workflow.sh push
```

## 🛠️ Available Scripts

### **Production Scripts**
- `./deploy-production.sh` - Deploy to production server
- `./status.sh` - Check production status
- `./backup-database.sh` - Backup database
- `./git-workflow.sh` - Git management workflow

### **Development Scripts**
- `./deploy-dev.sh` - Set up development environment
- `./start-dev.sh` - Start development server
- `./cleanup-repository.sh` - Clean up repository

### **Git Workflow Commands**
```bash
./git-workflow.sh status     # Check repository and service status
./git-workflow.sh commit     # Commit changes with message
./git-workflow.sh push       # Push to remote repository
./git-workflow.sh pull       # Pull from remote repository
./git-workflow.sh deploy     # Deploy to production
./git-workflow.sh update     # Pull and deploy
./git-workflow.sh backup     # Create backup
./git-workflow.sh clean      # Clean repository
```

## 🌐 Access URLs

### **Production (Live)**
- **Main Portal**: https://fishing.thepeaveys.net
- **Weather Page**: https://fishing.thepeaveys.net/weather.html
- **Locations Page**: https://fishing.thepeaveys.net/locations.html
- **Forecast Page**: https://fishing.thepeaveys.net/forecast.html

### **Development (Local)**
- **Main Portal**: http://localhost:5000
- **Weather Page**: http://localhost:5000/weather.html
- **Locations Page**: http://localhost:5000/locations.html
- **Forecast Page**: http://localhost:5000/forecast.html

## 📊 Monitoring & Maintenance

### **Check Service Status**
```bash
# Check application service
sudo systemctl status fishing-weather

# Check Apache web server
sudo systemctl status httpd

# View application logs
sudo journalctl -u fishing-weather -f

# View Apache logs
sudo tail -f /var/log/httpd/fishing-weather-ssl-access.log
```

### **Database Management**
```bash
# View database statistics
python3 -c "from working_database import WorkingWeatherDatabase; db = WorkingWeatherDatabase(); print(db.get_statistics())"

# Backup database
./backup-database.sh

# Reset database (if needed)
rm weather_data.db
python3 working_database.py
```

### **SSL Certificate Management**
```bash
# Check SSL configuration
./check-ssl-config.sh

# Renew Let's Encrypt certificate
sudo certbot renew

# Check certificate expiration
sudo openssl x509 -in /etc/letsencrypt/live/fishing.thepeaveys.net/cert.pem -noout -dates
```

## 🔧 Configuration Files

### **Application Configuration**
- **Main App**: `/home/typeavey/fishing-weather/app.py`
- **Weather API**: `/home/typeavey/fishing-weather/fishing.py`
- **Database**: `/home/typeavey/fishing-weather/working_database.py`
- **Settings**: `/home/typeavey/fishing-weather/settings.json`
- **API Config**: `/home/typeavey/fishing-weather/config.json`

### **System Configuration**
- **Systemd Service**: `/etc/systemd/system/fishing-weather.service`
- **Apache Config**: `/etc/httpd/conf.d/fishing-weather.conf`
- **SSL Certificate**: `/etc/letsencrypt/live/fishing.thepeaveys.net/`

## 🚨 Troubleshooting

### **Common Issues**

1. **Service Not Starting**
   ```bash
   sudo systemctl status fishing-weather
   sudo journalctl -u fishing-weather -f
   ```

2. **Database Errors**
   ```bash
   sudo chown typeavey:typeavey weather_data.db
   chmod 644 weather_data.db
   ```

3. **Apache Errors**
   ```bash
   sudo apachectl configtest
   sudo tail -f /var/log/httpd/fishing-weather-ssl-error.log
   ```

4. **SSL Certificate Issues**
   ```bash
   ./check-ssl-config.sh
   sudo certbot --apache -d fishing.thepeaveys.net
   ```

### **Reset Procedures**

1. **Reset Application**
   ```bash
   sudo systemctl restart fishing-weather
   ```

2. **Reset Apache**
   ```bash
   sudo systemctl restart httpd
   ```

3. **Reset Database**
   ```bash
   rm weather_data.db
   python3 working_database.py
   ```

## 📈 Performance Monitoring

### **Application Metrics**
- **Memory Usage**: Check with `sudo systemctl status fishing-weather`
- **Database Size**: Check with `ls -lh weather_data.db`
- **Log Growth**: Monitor log file sizes in `/var/log/httpd/`

### **Web Server Metrics**
- **Apache Status**: `sudo systemctl status httpd`
- **SSL Certificate**: Check expiration dates
- **Access Logs**: Monitor traffic patterns

## 🔄 Update Procedures

### **Regular Updates**
```bash
# 1. Make your changes
# 2. Test locally (optional)
./deploy-dev.sh
./start-dev.sh

# 3. Deploy to production
./deploy-production.sh

# 4. Verify deployment
./status.sh
```

### **Emergency Updates**
```bash
# Quick deployment without testing
./deploy-production.sh

# Check status immediately
./status.sh
```

### **Git Workflow Updates**
```bash
# Complete workflow
./git-workflow.sh commit 'Update description'
./git-workflow.sh push
./git-workflow.sh deploy
```

## 🎯 Best Practices

### **Development**
1. **Always test changes** before deploying to production
2. **Use descriptive commit messages** for better tracking
3. **Backup database** before major changes
4. **Monitor logs** after deployments

### **Production**
1. **Deploy during low-traffic periods**
2. **Monitor service status** after deployments
3. **Keep backups** of important data
4. **Document changes** for future reference

### **Security**
1. **Keep SSL certificates updated**
2. **Monitor access logs** for unusual activity
3. **Regular security updates** for system packages
4. **Backup configuration files** before changes

## 🎉 Success Checklist

- ✅ **Repository cleaned** of Mac/localhost references
- ✅ **Production deployment script** created
- ✅ **Git workflow** established
- ✅ **Monitoring scripts** in place
- ✅ **Backup procedures** configured
- ✅ **SSL/HTTPS** working properly
- ✅ **Service management** automated
- ✅ **Documentation** updated

## 🎣 Happy Fishing!

Your fishing weather portal is now **production-ready** with a streamlined development workflow. You can continue developing and deploying with confidence!

**🌐 Live Portal**: https://fishing.thepeaveys.net
**📊 Status Check**: `./status.sh`
**🚀 Deploy Updates**: `./deploy-production.sh`
