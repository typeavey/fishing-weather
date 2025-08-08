# Fishing Information Portal

A modern, interactive fishing information portal with modular weather components and real-time weather data integration.

## 🌟 Features

- **Interactive Dashboard**: Modern, responsive design with real-time weather data
- **Modular Weather Components**: Embeddable weather widgets for other websites
- **REST API**: Full API for integrating weather data into other applications
- **Real-time Updates**: Automatic data refresh and caching
- **Location Filtering**: Filter weather data by location and fishing conditions
- **Mobile Responsive**: Works seamlessly on desktop, tablet, and mobile devices

## 🏗️ Architecture

### Frontend Components

1. **Main Portal** (`index.html`)
   - Interactive dashboard with weather overview
   - Location and condition filtering
   - Real-time data updates

2. **Weather Module** (`weather-module.html`)
   - Standalone weather component
   - Can be embedded in other websites
   - Full filtering and refresh capabilities

3. **Weather Widget** (`weather-widget.html`)
   - Lightweight embeddable widget
   - Perfect for sidebar integration
   - Minimal footprint

### Backend API

1. **Flask API Server** (`app.py`)
   - RESTful API endpoints
   - Data caching for performance
   - CORS support for cross-origin requests

2. **Weather Data Processing**
   - Real-time weather data fetching
   - Fishing condition analysis
   - Data transformation and formatting

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd fishing-weather
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your API key**
   Edit `config.json` and add your OpenWeatherMap API key:
   ```json
   {
     "api_key": "your_openweathermap_api_key_here",
     "output_dir": "./fishing-website"
   }
   ```

4. **Start the API server**
   ```bash
   python app.py
   ```

5. **Access the portal**
   Open your browser and navigate to:
   - Main Portal: `http://localhost:5000`
   - Weather Module: `http://localhost:5000/weather-module`
   - Weather Widget: `http://localhost:5000/weather-widget`

## 📊 API Endpoints

### Weather Data

- `GET /api/weather` - Get all weather data
- `GET /api/forecast?location=<location>` - Get forecast for specific location
- `GET /api/locations` - Get all available locations
- `GET /weather-data.json` - Static weather data (fallback)

### Health & Status

- `GET /api/health` - API health check

## 🔧 Configuration

### Weather Thresholds

Edit `settings.json` to customize fishing condition thresholds:

```json
{
  "thresholds": {
    "wind_speed": {
      "great": 5,
      "good_min": 5.1,
      "good_max": 8,
      "bad_min": 8.1,
      "bad_max": 10
    },
    "wind_gust": {
      "gusty": 15
    },
    "temp": {
      "cold_max": 50,
      "hot_min": 80
    },
    "pressure": 29.92
  }
}
```

### Locations

Add or modify fishing locations in `settings.json`:

```json
{
  "locations": {
    "Location Name": {
      "lat": "43.6406",
      "lon": "-72.1440"
    }
  }
}
```

## 🎨 Customization

### Styling

The portal uses CSS custom properties for easy theming. Key variables:

```css
:root {
  --primary-color: #2563eb;
  --secondary-color: #1e40af;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --danger-color: #ef4444;
}
```

### Embedding Weather Components

#### Weather Module

```html
<iframe src="http://localhost:5000/weather-module" 
        width="100%" 
        height="600px" 
        frameborder="0">
</iframe>
```

#### Weather Widget

```html
<iframe src="http://localhost:5000/weather-widget" 
        width="400px" 
        height="300px" 
        frameborder="0">
</iframe>
```

## 🔄 Data Flow

1. **Data Collection**: Python script fetches weather data from OpenWeatherMap API
2. **Processing**: Data is processed and fishing conditions are calculated
3. **Caching**: Processed data is cached for 5 minutes to reduce API calls
4. **API Serving**: Flask API serves data to frontend components
5. **Frontend Display**: JavaScript components render and filter the data

## 🛠️ Development

### Project Structure

```
fishing-weather/
├── app.py                 # Flask API server
├── fishing.py            # Core weather processing logic
├── config.json           # API configuration
├── settings.json         # Locations and thresholds
├── requirements.txt      # Python dependencies
├── fishing-website/      # Frontend components
│   ├── index.html        # Main portal
│   ├── weather-module.html  # Standalone weather module
│   ├── weather-widget.html  # Embeddable widget
│   └── js/
│       └── weather-api.js   # JavaScript API module
└── README.md             # This file
```

### Adding New Features

1. **New Weather Component**: Create new HTML file in `fishing-website/`
2. **API Endpoint**: Add new route in `app.py`
3. **Data Processing**: Extend functions in `fishing.py`
4. **Frontend Logic**: Add JavaScript in appropriate component

## 🔍 Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure your OpenWeatherMap API key is valid
   - Check `config.json` for correct key format

2. **Port Already in Use**
   - Change port in `app.py` line 150
   - Or kill existing process using port 5000

3. **CORS Issues**
   - Ensure Flask-CORS is installed
   - Check browser console for CORS errors

4. **Data Not Loading**
   - Check API server is running
   - Verify network connectivity
   - Check browser console for errors

### Logs

The application logs to console with different levels:
- `INFO`: General information
- `DEBUG`: Detailed debugging information
- `WARNING`: Non-critical issues
- `ERROR`: Critical errors

## 📈 Performance

- **Caching**: 5-minute cache reduces API calls
- **Compression**: Gzip compression for faster loading
- **CDN**: Font Awesome and Google Fonts loaded from CDN
- **Lazy Loading**: Data loaded on demand

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎣 Happy Fishing!

Enjoy your new interactive fishing information portal! 🐟
