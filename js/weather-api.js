/**
 * Weather API Module for Fishing Information Portal
 * This module handles communication with the Python backend
 */

class WeatherAPI {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
        this.endpoints = {
            weather: '/api/weather',
            forecast: '/api/forecast',
            locations: '/api/locations'
        };
    }

    /**
     * Fetch weather data for all locations
     * @returns {Promise<Array>} Weather data array
     */
    async fetchWeatherData() {
        try {
            const response = await fetch(`${this.baseUrl}/api/weather`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching weather data:', error);
            throw error;
        }
    }

    /**
     * Fetch forecast data for a specific location
     * @param {string} location - Location name
     * @returns {Promise<Array>} Forecast data array
     */
    async fetchForecastData(location) {
        try {
            const response = await fetch(`${this.baseUrl}/api/forecast?location=${encodeURIComponent(location)}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching forecast data:', error);
            throw error;
        }
    }

    /**
     * Fetch all available locations
     * @returns {Promise<Array>} Locations array
     */
    async fetchLocations() {
        try {
            const response = await fetch(`${this.baseUrl}/api/locations`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching locations:', error);
            throw error;
        }
    }

    /**
     * Fetch weather data from the static JSON file (fallback)
     * @returns {Promise<Array>} Weather data array
     */
    async fetchStaticWeatherData() {
        try {
            const response = await fetch(`${this.baseUrl}/weather-data.json`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching static weather data:', error);
            throw error;
        }
    }
}

/**
 * Weather Data Processor
 * Handles data transformation and formatting
 */
class WeatherDataProcessor {
    /**
     * Process raw weather data into display format
     * @param {Array} rawData - Raw weather data from API
     * @returns {Array} Processed weather data
     */
    static processWeatherData(rawData) {
        return rawData.map(item => ({
            location: item.location,
            date: this.formatDate(item.date_ts),
            sunrise: item.sunrise,
            summary: item.summary,
            temp: item.temp,
            pressure: item.pressure,
            windSpeed: item.wind_speed,
            windGust: item.wind_gust,
            fishing: item.fishing,
            fishingBase: this.extractFishingBase(item.fishing),
            badgeClass: this.getBadgeClass(item.fishing_base)
        }));
    }

    /**
     * Format date for display
     * @param {string|Date} date - Date to format
     * @returns {string} Formatted date
     */
    static formatDate(date) {
        const d = new Date(date);
        return d.toLocaleDateString('en-US', {
            weekday: 'long',
            month: '2-digit',
            day: '2-digit',
            year: 'numeric'
        });
    }

    /**
     * Extract fishing base condition from full fishing description
     * @param {string} fishing - Full fishing description
     * @returns {string} Fishing base condition
     */
    static extractFishingBase(fishing) {
        if (fishing.includes('Great Fishing')) return 'Great';
        if (fishing.includes('Good Fishing')) return 'Good';
        if (fishing.includes('Tough Fishing')) return 'Tough';
        if (fishing.includes('Stay Home')) return 'Stay Home';
        return 'Unknown';
    }

    /**
     * Get badge CSS class based on fishing condition
     * @param {string} fishingBase - Fishing base condition
     * @returns {string} Badge CSS class
     */
    static getBadgeClass(fishingBase) {
        const classes = {
            'Great': 'badge-great',
            'Good': 'badge-good',
            'Tough': 'badge-tough',
            'Stay Home': 'badge-stay-home'
        };
        return classes[fishingBase] || 'badge-unknown';
    }

    /**
     * Group weather data by date
     * @param {Array} weatherData - Weather data array
     * @returns {Object} Grouped weather data
     */
    static groupByDate(weatherData) {
        const grouped = {};
        weatherData.forEach(item => {
            if (!grouped[item.date]) {
                grouped[item.date] = [];
            }
            grouped[item.date].push(item);
        });
        return grouped;
    }

    /**
     * Filter weather data by location and condition
     * @param {Array} weatherData - Weather data array
     * @param {string} location - Location filter
     * @param {string} condition - Condition filter
     * @returns {Array} Filtered weather data
     */
    static filterData(weatherData, location = '', condition = '') {
        return weatherData.filter(item => {
            const locationMatch = !location || item.location === location;
            const conditionMatch = !condition || item.fishingBase === condition;
            return locationMatch && conditionMatch;
        });
    }
}

/**
 * Weather Module Class
 * Main class for managing weather display and interactions
 */
class WeatherModule {
    constructor(containerId = 'weatherModule', options = {}) {
        this.container = document.getElementById(containerId);
        this.api = new WeatherAPI(options.baseUrl || '');
        this.weatherData = [];
        this.filteredData = [];
        this.options = {
            autoRefresh: options.autoRefresh || false,
            refreshInterval: options.refreshInterval || 300000, // 5 minutes
            ...options
        };
        
        if (!this.container) {
            throw new Error(`Container with ID '${containerId}' not found`);
        }
        
        this.init();
    }

    /**
     * Initialize the weather module
     */
    init() {
        this.setupEventListeners();
        this.loadWeatherData();
        
        if (this.options.autoRefresh) {
            this.startAutoRefresh();
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        const refreshBtn = this.container.querySelector('#refreshBtn');
        const locationFilter = this.container.querySelector('#locationFilter');
        const conditionFilter = this.container.querySelector('#conditionFilter');

        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadWeatherData());
        }
        if (locationFilter) {
            locationFilter.addEventListener('change', () => this.filterData());
        }
        if (conditionFilter) {
            conditionFilter.addEventListener('change', () => this.filterData());
        }
    }

    /**
     * Load weather data
     */
    async loadWeatherData() {
        const weatherContent = this.container.querySelector('#weatherContent');
        weatherContent.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                Loading weather data...
            </div>
        `;

        try {
            // Try to fetch from API first, fallback to static data
            try {
                this.weatherData = await this.api.fetchWeatherData();
            } catch (apiError) {
                console.warn('API not available, using static data:', apiError);
                this.weatherData = await this.api.fetchStaticWeatherData();
            }

            this.weatherData = WeatherDataProcessor.processWeatherData(this.weatherData);
            this.filteredData = [...this.weatherData];
            this.renderWeatherData();
        } catch (error) {
            weatherContent.innerHTML = `
                <div class="error-message">
                    <p>Error loading weather data. Please try again.</p>
                    <button class="refresh-btn" onclick="weatherModule.loadWeatherData()">Retry</button>
                </div>
            `;
        }
    }

    /**
     * Filter data based on selected filters
     */
    filterData() {
        const locationFilter = this.container.querySelector('#locationFilter')?.value || '';
        const conditionFilter = this.container.querySelector('#conditionFilter')?.value || '';

        this.filteredData = WeatherDataProcessor.filterData(
            this.weatherData,
            locationFilter,
            conditionFilter
        );

        this.renderWeatherData();
    }

    /**
     * Render weather data
     */
    renderWeatherData() {
        const weatherContent = this.container.querySelector('#weatherContent');
        
        if (this.filteredData.length === 0) {
            weatherContent.innerHTML = `
                <div class="no-data">
                    <p>No weather data found for the selected filters.</p>
                </div>
            `;
            return;
        }

        const groupedByDate = WeatherDataProcessor.groupByDate(this.filteredData);
        let html = '';
        
        Object.entries(groupedByDate).forEach(([date, items]) => {
            html += `
                <div style="margin-bottom: 1.5rem;">
                    <h3 style="color: var(--gray-700); margin-bottom: 1rem; border-bottom: 2px solid var(--gray-200); padding-bottom: 0.5rem; font-size: 1.1rem;">
                        ${date}
                    </h3>
                    <div class="weather-grid">
            `;

            items.forEach(item => {
                html += `
                    <div class="weather-card">
                        <div class="weather-card-header">
                            <span class="location-name">${item.location}</span>
                            <span class="fishing-badge ${item.badgeClass}">${item.fishingBase}</span>
                        </div>
                        <div class="weather-details">
                            <div class="weather-detail">
                                <span class="weather-detail-label">Sunrise:</span>
                                <span class="weather-detail-value">${item.sunrise}</span>
                            </div>
                            <div class="weather-detail">
                                <span class="weather-detail-label">Temperature:</span>
                                <span class="weather-detail-value">${item.temp}°F</span>
                            </div>
                            <div class="weather-detail">
                                <span class="weather-detail-label">Wind Speed:</span>
                                <span class="weather-detail-value">${item.windSpeed} mph</span>
                            </div>
                            <div class="weather-detail">
                                <span class="weather-detail-label">Wind Gust:</span>
                                <span class="weather-detail-value">${item.windGust} mph</span>
                            </div>
                            <div class="weather-detail">
                                <span class="weather-detail-label">Pressure:</span>
                                <span class="weather-detail-value">${item.pressure} inHg</span>
                            </div>
                            <div class="weather-detail">
                                <span class="weather-detail-label">Conditions:</span>
                                <span class="weather-detail-value">${item.summary}</span>
                            </div>
                        </div>
                    </div>
                `;
            });

            html += `
                    </div>
                </div>
            `;
        });

        weatherContent.innerHTML = html;
    }

    /**
     * Start auto-refresh functionality
     */
    startAutoRefresh() {
        this.refreshInterval = setInterval(() => {
            this.loadWeatherData();
        }, this.options.refreshInterval);
    }

    /**
     * Stop auto-refresh functionality
     */
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    /**
     * Destroy the weather module
     */
    destroy() {
        this.stopAutoRefresh();
        // Remove event listeners if needed
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { WeatherAPI, WeatherDataProcessor, WeatherModule };
}
