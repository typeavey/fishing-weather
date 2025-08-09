# 🎣 Stocking Reports Feature

## Overview

The Stocking Reports feature integrates NH Fish & Game stocking data into your fishing portal, providing real-time information about when and where fish have been stocked in your favorite lakes.

## 🌟 Features

### ✅ **Automatic Data Updates**
- **Daily Updates**: Automatically fetches new stocking data every day at 6:00 AM
- **API Integration**: Connects to NH Fish & Game ArcGIS services
- **Fallback Data**: Uses sample data when API is unavailable
- **Update Logging**: Tracks all update attempts and results

### ✅ **Interactive Stocking Page**
- **Filter by Lake**: View stocking data for specific lakes
- **Time Periods**: Filter by last 7, 30, 90 days, or full year
- **Real-time Updates**: Manual refresh and update buttons
- **Status Monitoring**: Shows last update time and success status

### ✅ **Rich Data Display**
- **Stocking Details**: Species, quantity, fish size, dates
- **Location Information**: Coordinates and specific stocking areas
- **Notes & Comments**: Additional stocking information
- **Visual Cards**: Beautiful, responsive card layout

## 📊 Data Sources

### **Primary Source: NH Fish & Game ArcGIS API**
- **URL**: `https://nhfg.maps.arcgis.com/apps/webappviewer/index.html?id=ce89fbd1ba0c4205ae6794dfb4c9f088`
- **API Endpoints**: 
  - `https://nhfg.maps.arcgis.com/rest/services/Stocking_Report/MapServer/0`
  - `https://services1.arcgis.com/RbMX0mRVOFNTdLzd/arcgis/rest/services/Stocking_Report/FeatureServer/0`

### **Fallback: Sample Data**
When API data is unavailable, the system uses realistic sample data for:
- **Winnipesaukee**: Rainbow Trout, 500 fish, 8-10 inches
- **Newfound**: Lake Trout, 300 fish, 12-14 inches
- **Squam**: Brook Trout, 400 fish, 6-8 inches
- **Champlain**: Brown Trout, 600 fish, 10-12 inches
- **Mascoma**: Rainbow Trout, 250 fish, 8-10 inches
- **Sunapee**: Lake Trout, 350 fish, 12-14 inches
- **First Connecticut**: Brook Trout, 200 fish, 6-8 inches

## 🔧 Technical Implementation

### **Backend Components**

#### **`stocking_data.py`**
```python
class NHStockingData:
    """Handles NH Fish & Game stocking data"""
    
    def __init__(self, db_path: str = "stocking_data.db"):
        # Initialize database and API URLs
    
    def update_stocking_data(self) -> Dict:
        # Fetch and parse stocking data
    
    def get_stocking_data(self, lake_name: str = None, days_back: int = 30) -> List[Dict]:
        # Retrieve stocking data from database
```

#### **Database Schema**
```sql
-- Stocking records table
CREATE TABLE stocking_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lake_name TEXT NOT NULL,
    species TEXT NOT NULL,
    stocking_date DATE NOT NULL,
    fish_size TEXT,
    quantity INTEGER,
    latitude REAL,
    longitude REAL,
    notes TEXT,
    source TEXT DEFAULT 'NH Fish & Game',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Update log table
CREATE TABLE update_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    update_type TEXT NOT NULL,
    records_updated INTEGER DEFAULT 0,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **API Endpoints**

#### **GET `/api/stocking`**
- **Purpose**: Retrieve stocking data
- **Parameters**: 
  - `lake` (optional): Filter by specific lake
  - `days` (optional): Number of days back (default: 30)
- **Response**: Array of stocking records

#### **POST `/api/stocking/update`**
- **Purpose**: Manually trigger stocking data update
- **Response**: Update result with success status and record count

#### **GET `/api/stocking/status`**
- **Purpose**: Get last update status
- **Response**: Update status with timestamp and success info

### **Frontend Components**

#### **`stocking.html`**
- **Responsive Design**: Works on desktop and mobile
- **Interactive Filters**: Lake and time period selection
- **Real-time Updates**: Manual refresh and update buttons
- **Status Monitoring**: Shows update status and last update time

## 🚀 How It Updates Itself

### **1. Automatic Daily Updates**
```bash
# Cron job runs daily at 6:00 AM
0 6 * * * /home/typeavey/fishing-weather/update-stocking.sh update >> /home/typeavey/logs/stocking_update.log 2>&1
```

### **2. Manual Updates**
```bash
# Update stocking data manually
./update-stocking.sh update

# Check update status
./update-stocking.sh status

# Test the module
./update-stocking.sh test
```

### **3. Web Interface Updates**
- **"Update from NH Fish & Game"** button on stocking page
- **Real-time status** display
- **Automatic refresh** after successful updates

### **4. Update Process**
1. **API Connection**: Attempts to connect to NH Fish & Game APIs
2. **Data Parsing**: Parses ArcGIS JSON responses
3. **Database Storage**: Saves records to SQLite database
4. **Logging**: Records update attempts and results
5. **Fallback**: Uses sample data if API fails

## 📈 Benefits for Anglers

### **🎯 Strategic Fishing**
- **Know When Lakes Were Stocked**: Plan trips around recent stockings
- **Target Specific Species**: Different techniques for different fish
- **Find the Best Spots**: Stocking location information
- **Size-based Strategies**: Target specific fish sizes

### **📊 Data-driven Decisions**
- **Stocking Schedules**: Understand when to expect new fish
- **Species Information**: Know what fish are in each lake
- **Quantity Data**: Understand stocking density
- **Historical Patterns**: Track stocking over time

### **🎣 Enhanced Success**
- **Recent Stockings**: Target areas with fresh fish
- **Species-specific Techniques**: Use appropriate lures and methods
- **Size Targeting**: Match gear to fish size
- **Location Intelligence**: Fish where fish were stocked

## 🔍 Troubleshooting

### **Common Issues**

#### **No Stocking Data Displayed**
```bash
# Check if database has data
./update-stocking.sh status

# Force update with sample data
./update-stocking.sh update
```

#### **API Connection Issues**
```bash
# Test API connectivity
curl -s "https://nhfg.maps.arcgis.com/rest/services/Stocking_Report/MapServer/0"

# Check logs
tail -f /home/typeavey/logs/stocking_update.log
```

#### **Database Issues**
```bash
# Check database file
ls -la stocking_data.db

# Test database connection
python3 -c "from stocking_data import NHStockingData; sd = NHStockingData(); print(sd.get_update_status())"
```

### **Log Files**
- **Update Logs**: `/home/typeavey/logs/stocking_update.log`
- **Application Logs**: `sudo journalctl -u fishing-weather -f`
- **Database**: `stocking_data.db`

## 🛠️ Maintenance

### **Regular Tasks**
1. **Monitor Logs**: Check for update failures
2. **Verify Data**: Ensure sample data is current
3. **API Health**: Test NH Fish & Game API connectivity
4. **Database Backups**: Include in regular backup schedule

### **Update Procedures**
```bash
# Update stocking data
./update-stocking.sh update

# Check status
./update-stocking.sh status

# View recent logs
tail -20 /home/typeavey/logs/stocking_update.log
```

## 🎯 Future Enhancements

### **Potential Improvements**
1. **Email Notifications**: Alert when new stockings are detected
2. **Map Integration**: Show stocking locations on interactive map
3. **Species-specific Recommendations**: Fishing advice based on stocked species
4. **Historical Trends**: Analyze stocking patterns over time
5. **Mobile App**: Native mobile application for stocking data

### **Additional Data Sources**
1. **Vermont Fish & Wildlife**: Expand to include VT stocking data
2. **USGS Water Data**: Integrate water temperature and flow data
3. **Local Reports**: Community-sourced stocking information
4. **Social Media**: Monitor fishing reports and photos

## 📞 Support

### **Getting Help**
- **Check Logs**: Review update logs for errors
- **Test API**: Verify NH Fish & Game API connectivity
- **Database Issues**: Check SQLite database integrity
- **Web Interface**: Test stocking page functionality

### **Useful Commands**
```bash
# Check service status
sudo systemctl status fishing-weather

# View application logs
sudo journalctl -u fishing-weather -f

# Test stocking API
curl -s "https://fishing.thepeaveys.net/api/stocking"

# Update stocking data
./update-stocking.sh update

# Check stocking status
./update-stocking.sh status
```

---

**🎣 The Stocking Reports feature provides anglers with critical information about when and where fish have been stocked, helping them make informed decisions about where and when to fish for the best success!**
