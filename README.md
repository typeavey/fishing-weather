# 🎣 Fishing Weather Portal

A comprehensive fishing weather information system providing real-time weather data, fishing conditions, and stocking information for 7 premier fishing locations across New Hampshire and Vermont.

## 🌟 Features

### 🎯 **Core Functionality**
- **Real-time Weather Data**: Current conditions and forecasts for all fishing locations
- **Fishing Condition Analysis**: AI-powered fishing condition ratings (Excellent, Great, Good, Fair, Moderate, Challenging, Difficult, Dangerous)
- **Multi-Location Support**: 7 premier fishing destinations
- **Stocking Information**: NH Fish & Game stocking data integration
- **Water Temperature Monitoring**: Multi-source water temperature data
- **Responsive Web Interface**: Modern, mobile-friendly design

### 📍 **Supported Locations**
1. **Lake Winnipesaukee** (43.6406, -72.1440) - NH's largest lake
2. **Newfound Lake** (43.7528, -71.7999) - Crystal clear waters
3. **Squam Lake** (43.8280, -71.5503) - Golden Pond fame
4. **Lake Champlain** (44.4896, -73.3582) - Border lake with VT
5. **Mascoma Lake** (43.6587, -72.3200) - Dartmouth area
6. **Lake Sunapee** (43.3770, -72.0850) - Mountain lake
7. **First Connecticut Lake** (45.0926, -71.2478) - Northern NH

### 🚀 **Technical Features**
- **RESTful API**: JSON endpoints for all data
- **Real-time Updates**: Auto-refresh weather data
- **Database Integration**: SQLite with optimized queries
- **Proxy Configuration**: Apache reverse proxy setup
- **SSL Support**: HTTPS encryption enabled

## ��️ Architecture

### **Frontend**
- **HTML5/CSS3**: Modern, responsive design
- **JavaScript**: ES6+ with async/await patterns
- **Weather API Module**: Comprehensive client-side data handling
- **Mobile-First**: Optimized for all device sizes

### **Backend**
- **Flask Framework**: Python-based REST API
- **SQLite Database**: Lightweight, efficient data storage
- **Virtual Environment**: Isolated Python dependencies
- **Multi-threaded**: Production-ready server configuration

### **Infrastructure**
- **Apache Web Server**: Static file serving and reverse proxy
- **SSL/TLS**: Let's Encrypt certificate management
- **Systemd Services**: Automated startup and management
- **Logging**: Comprehensive error and access logging

## 🚀 Quick Start

### **Prerequisites**
- Python 3.9+
- Apache 2.4+
- SQLite3
- Git

### **Installation**

1. **Clone the Repository**
   ```bash
   git clone https://github.com/typeavey/fishing-weather.git
   cd fishing-weather
   ```

2. **Set Up Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp config.json.template config.json
   # Edit config.json with your API keys
   ```

4. **Initialize Database**
   ```bash
   python3 -c "
   from working_database import WorkingWeatherDatabase
   from stocking_data import StockingData
   from water_temperature import WaterTemperature
   
   wdb = WorkingWeatherDatabase()
   sd = StockingData()
   wt = WaterTemperature()
   print('Databases initialized successfully!')
   "
   ```

5. **Start the Application**
   ```bash
   python3 app.py
   ```

### **Production Deployment**

1. **Apache Configuration**
   ```apache
   # Add to your virtual host configuration
   ProxyPreserveHost On
   ProxyPass /api/ http://localhost:5000/api/
   ProxyPassReverse /api/ http://localhost:5000/api/
   ```

2. **Systemd Service** (Optional)
   ```bash
   sudo cp start-flask.sh /usr/local/bin/
   sudo chmod +x /usr/local/bin/start-flask.sh
   ```

3. **SSL Certificate**
   ```bash
   sudo certbot --apache -d fishing.thepeaveys.net
   ```

## 📡 API Endpoints

### **Weather Data**
- `GET /api/weather` - Current weather for all locations
- `GET /api/forecast` - Weather forecasts
- `GET /api/locations` - Available fishing locations

### **Stocking Information**
- `GET /api/stocking` - NH Fish & Game stocking data

### **Response Format**
```json
{
  "location": "Winnipesaukee",
  "date_str": "Friday 08-08-2025",
  "temp_day": 79.23,
  "wind_speed": 4.45,
  "wind_gust": 4.5,
  "pressure": 30.24,
  "fishing_base": "Fair Fishing",
  "fishing_rating": "Fair Fishing",
  "summary": "Expect a day of partly cloudy with rain"
}
```

## 🗄️ Database Schema

### **Weather Data Table**
- Location coordinates and metadata
- Temperature, wind, pressure readings
- Fishing condition calculations
- Timestamp and forecast data

### **Stocking Records Table**
- Fish species and quantities
- Stocking dates and locations
- NH Fish & Game data integration

### **Water Temperature Table**
- Multi-source temperature data
- Historical temperature trends
- Location-specific monitoring

## 🔧 Configuration

### **config.json**
```json
{
  "api_key": "your_weather_api_key",
  "output_dir": "/var/www/fishing.thepeaveys.net/public_html"
}
```

### **settings.json**
- Location coordinates
- Weather thresholds
- Fishing condition parameters
- Customizable thresholds

## 🛠️ Development

### **File Structure**
```
public_html/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── config.json           # API configuration
├── settings.json         # Location settings
├── *.html               # Website pages
├── js/                  # JavaScript modules
├── sqlite_db/           # Database files
├── venv/                # Python virtual environment
└── start-flask.sh       # Startup script
```

### **Adding New Locations**
1. Add coordinates to `settings.json`
2. Update database queries
3. Test API endpoints
4. Update frontend display

### **Customizing Fishing Conditions**
- Modify thresholds in `settings.json`
- Adjust calculation logic in Python modules
- Update frontend rating display

## 🧪 Testing

### **API Testing**
```bash
# Test weather endpoint
curl -s "http://localhost:5000/api/weather" | head -3

# Test locations endpoint
curl -s "http://localhost:5000/api/locations"

# Test through proxy
curl -s -k "https://fishing.thepeaveys.net/api/weather"
```

### **Website Testing**
- Visit `https://fishing.thepeaveys.net/`
- Check API calls in browser console
- Verify mobile responsiveness
- Test all fishing location pages

## 🚀 Deployment

### **Production Checklist**
- [ ] SSL certificate installed
- [ ] Apache proxy configured
- [ ] Flask app running as service
- [ ] Database permissions set
- [ ] Log rotation configured
- [ ] Backup system in place

### **Monitoring**
- Check Apache error logs: `/var/log/httpd/fishing_error.log`
- Monitor Flask application logs
- Database performance monitoring
- SSL certificate expiration alerts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### **Development Guidelines**
- Follow PEP 8 Python style guide
- Add comprehensive error handling
- Include logging for debugging
- Update documentation for new features

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **NH Fish & Game**: Stocking data and information
- **Weather API Providers**: Real-time weather data
- **Open Source Community**: Flask, Apache, and other tools
- **Fishing Community**: Feedback and feature requests

## 📞 Support

- **Website**: [https://fishing.thepeaveys.net](https://fishing.thepeaveys.net)
- **Issues**: [GitHub Issues](https://github.com/typeavey/fishing-weather/issues)
- **Documentation**: This README and inline code comments

---

**Happy Fishing! 🎣🌤️**

*Built with ❤️ for the New Hampshire and Vermont fishing community*
