# 🔄 Quick Update Reference

## 🚀 **One-Command Update**
```bash
cd /home/typeavey/fishing-weather
./update-deployment.sh
```

## 📋 **Manual Update Steps**
```bash
# 1. Backup database
./backup-database.sh

# 2. Pull changes
git pull origin main

# 3. Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# 4. Update web files
sudo cp -r fishing-website/* /var/www/fishing.thepeaveys.net/public_html/
sudo chown -R typeavey:typeavey /var/www/fishing.thepeaveys.net/public_html

# 5. Restart application
sudo systemctl restart fishing-weather

# 6. Verify update
curl http://localhost:5000/api/health
```

## 🔍 **Check Status**
```bash
# Application status
sudo systemctl status fishing-weather

# View logs
sudo journalctl -u fishing-weather -f

# Test API
curl http://localhost:5000/api/health

# Check website
curl http://fishing.thepeaveys.net/api/health
```

## 🎯 **Common Update Scenarios**

### **Code Changes Only**
```bash
git pull origin main
sudo systemctl restart fishing-weather
```

### **Frontend Changes Only**
```bash
git pull origin main
sudo cp -r fishing-website/* /var/www/fishing.thepeaveys.net/public_html/
```

### **Full Update (New Dependencies)**
```bash
./update-deployment.sh
```

## 🔄 **Rollback (If Needed)**
```bash
# Stop application
sudo systemctl stop fishing-weather

# Restore database
cp backups/weather_data_*.db weather_data.db

# Restore web files
sudo rm -rf /var/www/fishing.thepeaveys.net/public_html
sudo mv /var/www/fishing.thepeaveys.net/public_html.backup.* /var/www/fishing.thepeaveys.net/public_html

# Restart application
sudo systemctl start fishing-weather
```

## 📊 **Update Checklist**
- ✅ Database backed up
- ✅ Git changes pulled
- ✅ Dependencies updated
- ✅ Static files copied
- ✅ Application restarted
- ✅ Health check passed
- ✅ Website accessible

## 🎣 **Quick Commands**
```bash
# Update everything
./update-deployment.sh

# Check status
sudo systemctl status fishing-weather

# View logs
sudo journalctl -u fishing-weather -f

# Test API
curl http://localhost:5000/api/health

# Backup database
./backup-database.sh
```

**🌐 Portal**: http://fishing.thepeaveys.net  
**📁 Code**: /home/typeavey/fishing-weather  
**🗄️ Database**: weather_data.db  
**🎣 Happy fishing!**
