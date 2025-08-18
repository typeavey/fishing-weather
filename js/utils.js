// ========================================
// 🎣 NH-VT Fishing Weather Website
// Shared JavaScript Utilities
// ========================================

// ========================================
// DATA FETCHING UTILITIES
// ========================================

/**
 * Fetch data from API endpoint with error handling
 * @param {string} endpoint - API endpoint to fetch from
 * @param {Object} options - Fetch options
 * @returns {Promise<Object>} - Parsed JSON response
 */
async function fetchData(endpoint, options = {}) {
    console.log(`🚀 fetchData called with endpoint: ${endpoint}`);
    console.log(`🌐 Current location: ${window.location.href}`);
    
    // Try current origin first
    try {
        console.log(`📡 Attempting primary fetch from: ${endpoint}`);
        const startTime = Date.now();
        const resp1 = await fetch(endpoint, options);
        const endTime = Date.now();
        console.log(`⏱️ Primary fetch response time: ${endTime - startTime}ms`);
        console.log(`📊 Response status: ${resp1.status} ${resp1.statusText}`);
        
        if (!resp1.ok) {
            console.warn(`⚠️ Primary fetch failed with status: ${resp1.status}`);
            throw new Error(`HTTP ${resp1.status}: ${resp1.statusText}`);
        }
        
        const data1 = await resp1.json();
        console.log(`✅ Primary fetch successful: ${endpoint}`);
        console.log(`📊 Data type: ${typeof data1}, Length: ${Array.isArray(data1) ? data1.length : 'N/A'}`);
        return data1;
    } catch (primaryError) {
        console.warn(`⚠️ Primary fetch failed for ${endpoint}:`, primaryError);
        // Fallback to Flask default port (use same host, port 5000)
        try {
            const { protocol, hostname } = window.location;
            const fallbackBase = `${protocol}//${hostname}:5000`;
            const fallbackUrl = endpoint.startsWith('http') ? endpoint : `${fallbackBase}${endpoint}`;
            console.log(`🔁 Retrying via Flask port: ${fallbackUrl}`);
            const startTime = Date.now();
            const resp2 = await fetch(fallbackUrl, options);
            const endTime = Date.now();
            console.log(`⏱️ Fallback fetch response time: ${endTime - startTime}ms`);
            console.log(`📊 Fallback response status: ${resp2.status} ${resp2.statusText}`);
            
            if (!resp2.ok) {
                console.warn(`⚠️ Fallback fetch failed with status: ${resp2.status}`);
                throw new Error(`HTTP ${resp2.status}: ${resp2.statusText}`);
            }
            
            const data2 = await resp2.json();
            console.log(`✅ Fallback fetch successful: ${fallbackUrl}`);
            console.log(`📊 Fallback data type: ${typeof data2}, Length: ${Array.isArray(data2) ? data2.length : 'N/A'}`);
            return data2;
        } catch (fallbackError) {
            console.error(`❌ Fallback fetch failed for ${endpoint}:`, fallbackError);
            throw fallbackError;
        }
    }
}

/**
 * Load weather data from API
 * @returns {Promise<Array>} - Weather data array
 */
async function loadWeatherData() {
    console.log('🌤️ loadWeatherData() called');
    try {
        console.log('📡 Attempting to fetch from /api/weather');
        const data = await fetchData('/api/weather');
        console.log('✅ loadWeatherData() successful, returning data');
        return data;
    } catch (e) {
        console.warn('⚠️ API fetch failed, falling back to local weather-data.json:', e);
        try {
            console.log('📁 Attempting to load local weather-data.json');
            const resp = await fetch('/weather-data.json');
            if (!resp.ok) throw new Error(`HTTP ${resp.status}: ${resp.statusText}`);
            const localData = await resp.json();
            console.log('✅ Local weather-data.json loaded successfully');
            return localData;
        } catch (e2) {
            console.error('❌ Failed to load local weather-data.json', e2);
            throw e2;
        }
    }
}

/**
 * Load water temperature data from API
 * @returns {Promise<Object>} - Water temperature data object
 */
async function loadWaterTemperatureData() {
    return await fetchData('/api/water-temperature/latest');
}

/**
 * Load stocking data from API
 * @returns {Promise<Array>} - Stocking data array
 */
async function loadStockingData() {
    return await fetchData('/api/stocking');
}

// ========================================
// RATING UTILITIES
// ========================================

/**
 * Get fishing rating from fishing base data
 * @param {string} fishingBase - Fishing base rating string
 * @returns {string} - Normalized fishing rating
 */
function getFishingRating(fishingBase) {
    if (!fishingBase) return 'Unknown';
    
    // Handle numeric ratings
    if (typeof fishingBase === 'number') {
        if (fishingBase >= 8) return 'Excellent';
        if (fishingBase >= 6) return 'Great';
        if (fishingBase >= 4) return 'Good';
        if (fishingBase >= 2) return 'Fair';
        return 'Poor';
    }
    
    // Handle string ratings
    const rating = fishingBase.toString().toLowerCase();
    if (rating.includes('excellent')) return 'Excellent';
    if (rating.includes('great')) return 'Great';
    if (rating.includes('good')) return 'Good';
    if (rating.includes('fair')) return 'Fair';
    if (rating.includes('moderate')) return 'Moderate';
    if (rating.includes('poor')) return 'Poor';
    
    return 'Fair';
}

/**
 * Get rating color class based on rating
 * @param {string|number} rating - Fishing rating
 * @returns {string} - CSS class name for rating color
 */
function getRatingColor(rating) {
    if (typeof rating === 'number') {
        if (rating >= 8) return 'excellent';
        if (rating >= 6) return 'good';
        if (rating >= 4) return 'fair';
        return 'poor';
    }
    
    const ratingStr = rating.toString().toLowerCase();
    if (ratingStr.includes('excellent')) return 'excellent';
    if (ratingStr.includes('great')) return 'good';
    if (ratingStr.includes('good')) return 'good';
    if (ratingStr.includes('fair')) return 'fair';
    if (ratingStr.includes('moderate')) return 'fair';
    if (ratingStr.includes('poor')) return 'poor';
    
    return 'fair';
}

/**
 * Get detailed rating explanation based on weather conditions
 * @param {Object} item - Weather data item
 * @returns {string} - Human-readable explanation
 */
function getRatingExplanation(item) {
    if (!item) return 'No data available';
    
    const temp = item.temp_day;
    const windSpeed = item.wind_speed;
    const pressure = item.pressure;
    const summary = item.summary || '';
    
    let explanations = [];
    
    // WIND SPEED - PRIMARY FACTOR (heavily weighted)
    if (windSpeed) {
        if (windSpeed <= 4) {
            explanations.push('EXCELLENT wind conditions (0-4 mph) - Perfect for trolling');
        } else if (windSpeed <= 6) {
            explanations.push('GOOD wind conditions (4.1-6 mph) - Very fishable');
        } else if (windSpeed <= 8) {
            explanations.push('FAIR wind conditions (6.1-8 mph) - Manageable but challenging');
        } else if (windSpeed <= 10) {
            explanations.push('TOUGH wind conditions (8.1-10 mph) - Difficult for trolling');
        } else {
            explanations.push('HARD NO - Wind too strong (10.1+ mph) - Not recommended');
        }
    }
    
    // Temperature analysis (secondary factor)
    if (temp) {
        if (temp >= 75) {
            explanations.push('High temperature may reduce fish activity');
        } else if (temp >= 65 && temp < 75) {
            explanations.push('Optimal temperature for fishing');
        } else if (temp >= 50 && temp < 65) {
            explanations.push('Cool temperature, fish may be active');
        } else if (temp < 50) {
            explanations.push('Cold temperature may limit fish activity');
        }
    }
    
    // Pressure analysis (tertiary factor)
    if (pressure) {
        if (pressure >= 30.0) {
            explanations.push('High pressure - stable conditions');
        } else if (pressure >= 29.8) {
            explanations.push('Normal pressure - good conditions');
        } else {
            explanations.push('Low pressure - changing conditions');
        }
    }
    
    // Weather conditions analysis (minimal impact)
    if (summary) {
        if (summary.toLowerCase().includes('clear') || summary.toLowerCase().includes('sunny')) {
            explanations.push('Clear skies - good visibility');
        } else if (summary.toLowerCase().includes('cloudy') || summary.toLowerCase().includes('overcast')) {
            explanations.push('Cloudy conditions - fish may be more active');
        } else if (summary.toLowerCase().includes('rain') || summary.toLowerCase().includes('shower')) {
            explanations.push('Rainy conditions - may affect fishing');
        }
    }
    
    // If no specific explanations, provide general rating reason
    if (explanations.length === 0) {
        const rating = getFishingRating(item.fishing_base);
        if (rating === 'Excellent' || rating === 'Great') {
            explanations.push('Favorable conditions for fishing');
        } else if (rating === 'Good' || rating === 'Fair') {
            explanations.push('Moderate conditions for fishing');
        } else {
            explanations.push('Challenging conditions for fishing');
        }
    }
    
    return explanations.join('; ');
}

// ========================================
// DOM UTILITIES
// ========================================

/**
 * Safely get DOM element with error handling
 * @param {string} id - Element ID
 * @param {string} context - Context for error message
 * @returns {HTMLElement|null} - DOM element or null
 */
function getElement(id, context = 'page') {
    const element = document.getElementById(id);
    if (!element) {
        console.error(`❌ Element not found: ${id} in ${context}`);
    }
    return element;
}

/**
 * Show loading state for an element
 * @param {string} elementId - Element ID to show loading for
 * @param {string} message - Loading message
 */
function showLoading(elementId, message = 'Loading...') {
    const element = getElement(elementId);
    if (element) {
        element.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                ${message}
            </div>
        `;
    }
}

/**
 * Show error state for an element
 * @param {string} elementId - Element ID to show error for
 * @param {string} message - Error message
 * @param {Error} error - Error object for details
 */
function showError(elementId, message, error = null) {
    const element = getElement(elementId);
    if (element) {
        const errorDetails = error ? `<br><small style="color: #6b7280;">Error: ${error.message}</small>` : '';
        element.innerHTML = `
            <div class="loading">
                <i class="fas fa-exclamation-triangle" style="color: #ef4444; font-size: 1.5rem;"></i>
                <span>${message}</span>
                ${errorDetails}
            </div>
        `;
    }
}

/**
 * Show no data state for an element
 * @param {string} elementId - Element ID to show no data for
 * @param {string} message - No data message
 */
function showNoData(elementId, message = 'No data available') {
    const element = getElement(elementId);
    if (element) {
        element.innerHTML = `
            <div class="no-data">
                <p>${message}</p>
            </div>
        `;
    }
}

// ========================================
// DATE & TIME UTILITIES
// ========================================

/**
 * Format timestamp to readable date string
 * @param {string|number} timestamp - Timestamp to format
 * @returns {string} - Formatted date string
 */
function formatDate(timestamp) {
    if (!timestamp) return 'Unknown';
    
    try {
        const date = new Date(timestamp);
        return date.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch (error) {
        console.error('Error formatting date:', error);
        return 'Invalid Date';
    }
}

/**
 * Format timestamp to readable time string
 * @param {string|number} timestamp - Timestamp to format
 * @returns {string} - Formatted time string
 */
function formatTime(timestamp) {
    if (!timestamp) return 'Unknown';
    
    try {
        const date = new Date(timestamp);
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        console.error('Error formatting time:', error);
        return 'Invalid Time';
    }
}

// ========================================
// EXPORT UTILITIES
// ========================================

// Make utilities available globally
console.log('🔧 Creating FishingUtils object...');
window.FishingUtils = {
    fetchData,
    loadWeatherData,
    loadWaterTemperatureData,
    loadStockingData,
    getFishingRating,
    getRatingColor,
    getRatingExplanation,
    getElement,
    showLoading,
    showError,
    showNoData,
    formatDate,
    formatTime
};
console.log('✅ FishingUtils object created with functions:', Object.keys(window.FishingUtils));
console.log('🔍 FishingUtils.loadWeatherData type:', typeof window.FishingUtils.loadWeatherData);
