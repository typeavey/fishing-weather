# 🌡️ Water Temperature Feature

## Overview

The Water Temperature feature integrates real-time water temperature data from multiple sources (USGS, NOAA, and estimation models) into your fishing portal, providing anglers with critical information about water conditions for optimal fishing success.

## 🌟 Features

### ✅ **Multi-Source Data Integration**
- **USGS Water Data**: Real-time temperature readings from government monitoring stations
- **NOAA Buoy Data**: Live buoy readings for major lakes
- **Estimation Models**: Sophisticated models for lakes without direct measurements
- **Automatic Fallback**: Seamless switching between data sources

### ✅ **Comprehensive Lake Coverage**
- **7 Lakes**: Complete coverage for all your fishing locations
- **Real-time Updates**: Daily automatic updates at 7:00 AM
- **Historical Data**: Temperature trends and patterns
- **Source Transparency**: Clear indication of data source for each reading

### ✅ **Advanced Estimation Models**
- **Seasonal Patterns**: Accounts for seasonal temperature variations
- **Lake Characteristics**: Depth, surface area, and thermal dynamics
- **Air Temperature Correlation**: Uses air temperature to estimate water temperature
- **Lake-Specific Adjustments**: Customized models for each lake

## 📊 Data Sources

### **Primary Sources**

#### **USGS Water Data API**
- **URL**: `https://waterservices.usgs.gov/nwis/iv/`
- **Coverage**: Champlain, Sunapee, and other major lakes
- **Update Frequency**: Real-time (every 15-60 minutes)
- **Data Quality**: Government-verified measurements

#### **NOAA Buoy Data**
- **URL**: `https://www.ndbc.noaa.gov/data/realtime2/`
- **Coverage**: Lake Champlain (Buoy 45012)
- **Update Frequency**: Hourly
- **Additional Data**: Wind, waves, air temperature

### **Estimation Models**

#### **Lake-Specific Models**
```python
lake_adjustments = {
    "Winnipesaukee": {"base_temp": 15, "seasonal_range": 12, "depth_factor": 0.8},
    "Newfound": {"base_temp": 14, "seasonal_range": 11, "depth_factor": 0.7},
    "Squam": {"base_temp": 13, "seasonal_range": 10, "depth_factor": 0.6},
    "Champlain": {"base_temp": 16, "seasonal_range": 13, "depth_factor": 0.9},
    "Mascoma": {"base_temp": 17, "seasonal_range": 14, "depth_factor": 1.0},
    "Sunapee": {"base_temp": 14, "seasonal_range": 11, "depth_factor": 0.7},
    "First Connecticut": {"base_temp": 18, "seasonal_range": 15, "depth_factor": 1.1},
}
```

#### **Model Components**
- **Seasonal Patterns**: Cosine function based on day of year
- **Air Temperature Influence**: Lagged and dampened correlation
- **Depth Cooling**: Deeper lakes are cooler
- **Lake Characteristics**: Surface area, average depth, maximum depth

## 🔧 Technical Implementation

### **Backend Components**

#### **`water_temperature.py`**
```python
class WaterTemperatureData:
    """Handles water temperature data from multiple sources"""
    
    def __init__(self, db_path: str = "water_temperature.db"):
        # Initialize database and data sources
    
    def fetch_usgs_temperature(self, lake_name: str) -> Optional[WaterTemperatureRecord]:
        # Fetch from USGS API
    
    def fetch_noaa_temperature(self, lake_name: str) -> Optional[WaterTemperatureRecord]:
        # Fetch from NOAA buoy data
    
    def estimate_temperature(self, lake_name: str, air_temperature: float, date: datetime.date) -> WaterTemperatureRecord:
        # Estimate using sophisticated models
```

#### **Database Schema**
```sql
-- Water temperature records table
CREATE TABLE water_temperature_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lake_name TEXT NOT NULL,
    temperature_celsius REAL NOT NULL,
    temperature_fahrenheit REAL NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    source TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    depth REAL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Temperature update log table
CREATE TABLE temperature_update_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    update_type TEXT NOT NULL,
    records_updated INTEGER DEFAULT 0,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **API Endpoints**

#### **GET `/api/water-temperature`**
- **Purpose**: Retrieve water temperature data
- **Parameters**: 
  - `lake` (optional): Filter by specific lake
  - `days` (optional): Number of days back (default: 7)
- **Response**: Array of temperature records

#### **GET `/api/water-temperature/latest`**
- **Purpose**: Get latest temperature for each lake
- **Response**: Dictionary of lake temperatures

#### **POST `/api/water-temperature/update`**
- **Purpose**: Manually trigger temperature update
- **Response**: Update result with success status and sources used

### **Automation Scripts**

#### **`update-water-temperature.sh`**
```bash
# Update water temperatures
./update-water-temperature.sh update

# Check current status
./update-water-temperature.sh status

# Test data sources
./update-water-temperature.sh test
```

## 🚀 How It Updates Itself

### **1. Automatic Daily Updates**
```bash
# Cron job runs daily at 7:00 AM
0 7 * * * /home/typeavey/fishing-weather/update-water-temperature.sh update >> /home/typeavey/logs/water_temperature_update.log 2>&1
```

### **2. Multi-Source Priority**
1. **USGS Data**: Primary source for lakes with monitoring stations
2. **NOAA Buoy Data**: Secondary source for lakes with buoys
3. **Estimation Models**: Fallback for lakes without direct measurements

### **3. Update Process**
1. **Source Priority**: Try USGS first, then NOAA, then estimation
2. **Data Validation**: Check for reasonable temperature ranges
3. **Database Storage**: Save all readings with source information
4. **Logging**: Track update attempts and results

## 📈 Current Data Coverage

### **Real-Time Sources**
- **Champlain**: USGS monitoring station (25.8°C)
- **Sunapee**: USGS monitoring station (22.6°C)

### **Estimation Models**
- **Winnipesaukee**: 17.9°C (based on air temp and lake characteristics)
- **Newfound**: 16.2°C (deep lake, cooler temperatures)
- **Squam**: 16.2°C (mountain lake, cooler temperatures)
- **Mascoma**: 24.5°C (shallow lake, warmer temperatures)
- **First Connecticut**: 25.3°C (river system, warmer temperatures)

## 🎯 Benefits for Anglers

### **🎣 Strategic Fishing**
- **Temperature-based Techniques**: Different lures and methods for different temperatures
- **Fish Behavior Prediction**: Water temperature affects fish activity
- **Seasonal Planning**: Understand temperature patterns throughout the year
- **Location Selection**: Choose fishing spots based on water temperature

### **📊 Data-driven Decisions**
- **Optimal Fishing Times**: Fish are most active at certain temperatures
- **Species Targeting**: Different fish prefer different temperature ranges
- **Depth Strategies**: Temperature varies with depth
- **Seasonal Patterns**: Track temperature trends over time

### **🌡️ Temperature Guidelines**
- **Cold Water (0-15°C)**: Slow presentations, deep water
- **Cool Water (15-20°C)**: Moderate activity, mid-depth
- **Warm Water (20-25°C)**: High activity, shallow water
- **Hot Water (25°C+)**: Early morning/evening fishing

## 🔍 Troubleshooting

### **Common Issues**

#### **No Temperature Data Displayed**
```bash
# Check if database has data
./update-water-temperature.sh status

# Force update
./update-water-temperature.sh update
```

#### **API Connection Issues**
```bash
# Test USGS connectivity
curl -s "https://waterservices.usgs.gov/nwis/iv/?format=json&sites=04295000&parameterCd=00010"

# Test NOAA connectivity
curl -s "https://www.ndbc.noaa.gov/data/realtime2/45012.txt"

# Check logs
tail -f /home/typeavey/logs/water_temperature_update.log
```

#### **Database Issues**
```bash
# Check database file
ls -la water_temperature.db

# Test database connection
python3 -c "from water_temperature import WaterTemperatureData; wt = WaterTemperatureData(); print(wt.get_latest_temperatures())"
```

### **Log Files**
- **Update Logs**: `/home/typeavey/logs/water_temperature_update.log`
- **Application Logs**: `sudo journalctl -u fishing-weather -f`
- **Database**: `water_temperature.db`

## 🛠️ Maintenance

### **Regular Tasks**
1. **Monitor Logs**: Check for update failures
2. **Verify Data Sources**: Test USGS and NOAA connectivity
3. **Update Estimation Models**: Refine models based on new data
4. **Database Backups**: Include in regular backup schedule

### **Update Procedures**
```bash
# Update water temperatures
./update-water-temperature.sh update

# Check status
./update-water-temperature.sh status

# View recent logs
tail -20 /home/typeavey/logs/water_temperature_update.log
```

## 🎯 Future Enhancements

### **Potential Improvements**
1. **Thermocline Detection**: Identify temperature layers in deep lakes
2. **Temperature Maps**: Visual temperature distribution
3. **Forecasting Models**: Predict future temperature trends
4. **Mobile Alerts**: Notify when temperatures reach optimal fishing conditions
5. **Historical Analysis**: Long-term temperature pattern analysis

### **Additional Data Sources**
1. **Satellite Data**: Remote sensing temperature measurements
2. **Community Reports**: Angler-submitted temperature readings
3. **Local Monitoring**: Partner with local organizations
4. **IoT Sensors**: Deploy temperature sensors on popular lakes

## 📞 Support

### **Getting Help**
- **Check Logs**: Review update logs for errors
- **Test APIs**: Verify USGS and NOAA connectivity
- **Database Issues**: Check SQLite database integrity
- **Model Accuracy**: Validate estimation model results

### **Useful Commands**
```bash
# Check service status
sudo systemctl status fishing-weather

# View application logs
sudo journalctl -u fishing-weather -f

# Test water temperature API
curl -s "https://fishing.thepeaveys.net/api/water-temperature/latest"

# Update water temperatures
./update-water-temperature.sh update

# Check water temperature status
./update-water-temperature.sh status
```

---

**🌡️ The Water Temperature feature provides anglers with critical information about water conditions, helping them make informed decisions about when and where to fish for optimal success!**
