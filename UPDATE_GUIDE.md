# 🔄 Update Deployment Guide

## 🎯 **Quick Update Process**

### **Automated Update (Recommended)**
```bash
# Navigate to your code directory
cd /home/typeavey/fishing-weather

# Run the automated update script
./update-deployment.sh
```

This script will:
- ✅ Backup your database automatically
- ✅ Pull latest changes from Git
- ✅ Update Python dependencies
- ✅ Update static files in web directory
- ✅ Test the deployment
- ✅ Restart the application
- ✅ Verify everything is working

## 🚀 **Manual Update Process**

### **Step 1: Backup Database**
```bash
cd /home/typeavey/fishing-weather
./backup-database.sh
```

### **Step 2: Pull Latest Changes**
```bash
# Pull latest changes from Git
git pull origin main

# Check for any conflicts
git status
```

### **Step 3: Update Dependencies**
```bash
# Activate virtual environment
source venv/bin/activate

# Update Python dependencies
pip install -r requirements.txt
```

### **Step 4: Update Static Files**
```bash
# Backup current web files
sudo cp -r /var/www/fishing.thepeaveys.net/public_html /var/www/fishing.thepeaveys.net/public_html.backup.$(date +%Y%m%d_%H%M%S)

# Copy new static files
sudo cp -r fishing-website/* /var/www/fishing.thepeaveys.net/public_html/

# Set proper permissions
sudo chown -R typeavey:typeavey /var/www/fishing.thepeaveys.net/public_html
sudo chmod -R 755 /var/www/fishing.thepeaveys.net/public_html
```

### **Step 5: Test Deployment**
```bash
# Test the deployment
python3 test_deployment.py
```

### **Step 6: Restart Application**
```bash
# Restart the systemd service
sudo systemctl restart fishing-weather

# Check status
sudo systemctl status fishing-weather
```

### **Step 7: Verify Update**
```bash
# Test the application
curl http://localhost:5000/api/health

# Check the website
curl http://fishing.thepeaveys.net/api/health
```

## 🔄 **Update Scenarios**

### **Scenario 1: Code Changes Only**
```bash
# Pull changes and restart
cd /home/typeavey/fishing-weather
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart fishing-weather
```

### **Scenario 2: Frontend Changes Only**
```bash
# Update static files only
cd /home/typeavey/fishing-weather
git pull origin main
sudo cp -r fishing-website/* /var/www/fishing.thepeaveys.net/public_html/
sudo chown -R typeavey:typeavey /var/www/fishing.thepeaveys.net/public_html
```

### **Scenario 3: Database Schema Changes**
```bash
# Backup database first
cd /home/typeavey/fishing-weather
./backup-database.sh

# Pull changes and update
git pull origin main
source venv/bin/activate
pip install -r requirements.txt

# Test database changes
python3 -c "from working_database import WorkingWeatherDatabase; db = WorkingWeatherDatabase(); print('Database test successful')"

# Restart application
sudo systemctl restart fishing-weather
```

### **Scenario 4: Major Update (New Dependencies)**
```bash
# Full backup and update
cd /home/typeavey/fishing-weather
./backup-database.sh

# Pull changes
git pull origin main

# Recreate virtual environment (if needed)
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Update static files
sudo cp -r fishing-website/* /var/www/fishing.thepeaveys.net/public_html/
sudo chown -R typeavey:typeavey /var/www/fishing.thepeaveys.net/public_html

# Test and restart
python3 test_deployment.py
sudo systemctl restart fishing-weather
```

## 🔍 **Pre-Update Checklist**

### **Before Running Updates**
1. **Check Git Status**
   ```bash
   git status
   git log --oneline -5
   ```

2. **Check Current Version**
   ```bash
   # Check current commit
   git rev-parse HEAD
   
   # Check if there are updates
   git fetch origin
   git log HEAD..origin/main --oneline
   ```

3. **Check Application Status**
   ```bash
   sudo systemctl status fishing-weather
   curl http://localhost:5000/api/health
   ```

4. **Check Disk Space**
   ```bash
   df -h
   du -sh /home/typeavey/fishing-weather
   du -sh /var/www/fishing.thepeaveys.net/public_html
   ```

## 🎯 **Post-Update Verification**

### **Verify Update Success**
```bash
# Check application status
sudo systemctl status fishing-weather

# Test API endpoints
curl http://localhost:5000/api/health
curl http://fishing.thepeaveys.net/api/health

# Check website
curl -I http://fishing.thepeaveys.net/

# Check logs
sudo journalctl -u fishing-weather --since "5 minutes ago"
```

### **Rollback Plan**
If something goes wrong:

```bash
# Stop the application
sudo systemctl stop fishing-weather

# Restore database (if needed)
cd /home/typeavey/fishing-weather
cp backups/weather_data_*.db weather_data.db

# Restore web files (if needed)
sudo rm -rf /var/www/fishing.thepeaveys.net/public_html
sudo mv /var/www/fishing.thepeaveys.net/public_html.backup.* /var/www/fishing.thepeaveys.net/public_html

# Restart application
sudo systemctl start fishing-weather
```

## 📊 **Update Monitoring**

### **Check Update Status**
```bash
# View recent logs
sudo journalctl -u fishing-weather -f

# Check application health
curl http://localhost:5000/api/health | jq .

# Check database status
python3 -c "from working_database import WorkingWeatherDatabase; db = WorkingWeatherDatabase(); print(db.get_statistics())"
```

### **Performance Monitoring**
```bash
# Check system resources
htop
df -h
free -h

# Check application performance
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5000/api/health
```

## 🔄 **Automated Updates (Optional)**

### **Set Up Automated Updates**
```bash
# Create a cron job for daily updates (optional)
sudo crontab -e

# Add this line for daily updates at 2 AM
0 2 * * * cd /home/typeavey/fishing-weather && ./update-deployment.sh >> /var/log/fishing-weather-updates.log 2>&1
```

### **Update Notification**
```bash
# Create update notification script
cat > notify-update.sh << 'EOF'
#!/bin/bash
# Send notification when update is complete
echo "Fishing Weather Portal updated successfully at $(date)" | mail -s "Portal Update Complete" your-email@example.com
EOF

chmod +x notify-update.sh
```

## 🎯 **Best Practices**

### **Update Frequency**
- **Security Updates**: Apply immediately
- **Feature Updates**: Weekly or bi-weekly
- **Bug Fixes**: As needed
- **Database Updates**: Monthly (with full backup)

### **Update Timing**
- **Best Time**: 2-4 AM (low traffic)
- **Duration**: 5-10 minutes
- **Downtime**: Minimal (rolling restart)

### **Communication**
- **Notify Users**: If major changes
- **Test First**: On staging environment
- **Document Changes**: Update changelog

## 🎣 **Update Success Checklist**

- ✅ **Database backed up** before update
- ✅ **Git changes pulled** successfully
- ✅ **Dependencies updated** correctly
- ✅ **Static files copied** to web directory
- ✅ **Application restarted** successfully
- ✅ **Health check passed** (API responding)
- ✅ **Website accessible** at domain
- ✅ **Logs checked** for errors
- ✅ **Performance verified** (response times)
- ✅ **Users notified** (if major changes)

## 🚀 **Quick Commands Reference**

```bash
# Quick update
./update-deployment.sh

# Manual update
git pull && sudo systemctl restart fishing-weather

# Check status
sudo systemctl status fishing-weather

# View logs
sudo journalctl -u fishing-weather -f

# Test application
curl http://localhost:5000/api/health

# Backup database
./backup-database.sh

# Rollback (if needed)
sudo systemctl stop fishing-weather
git reset --hard HEAD~1
sudo systemctl start fishing-weather
```

## 🎉 **Update Complete!**

Your fishing weather portal is now **up-to-date** and ready for use!

**🌐 Portal**: http://fishing.thepeaveys.net  
**📊 Status**: All systems operational  
**🔄 Last Update**: $(date)  
**🎣 Happy fishing!**
