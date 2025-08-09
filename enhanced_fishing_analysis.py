#!/usr/bin/env python3
"""
Enhanced Fishing Condition Analysis
Incorporates wind speed, temperature, weather conditions, pressure, moon phase, and wind direction
"""

import datetime
import math
from typing import Dict, List, Tuple, Union, Optional

class EnhancedFishingAnalysis:
    """
    Enhanced fishing condition analysis incorporating multiple factors:
    - Wind speed and gusts (most important)
    - Temperature (comfort factor)
    - Weather conditions (clear/overcast/rain)
    - Pressure (low pressure improves fishing)
    - Moon phase (full moon is better)
    - Wind direction (helpful but not critical)
    """
    
    def __init__(self, thresholds: Optional[Dict] = None):
        """
        Initialize with custom thresholds or use defaults
        """
        self.thresholds = thresholds or {
            # Wind speed thresholds (mph) - Based on trolling requirements
            "wind_speed": {
                "excellent": 4,      # 0-4 mph: Excellent fishing (Perfect for trolling)
                "great": 6,          # 4.1-6 mph: Great fishing (Very fishable)
                "good": 8,           # 6.1-8 mph: Good fishing (Manageable but challenging)
                "moderate": 10,      # 8.1-10 mph: Moderate fishing (Difficult for trolling)
                "challenging": 10.1, # 10.1+ mph: Challenging (Hard no - not recommended)
                "difficult": 15,     # 15+ mph: Difficult
                "dangerous": 20      # 20+ mph: Dangerous/Stay home
            },
            # Wind gust thresholds (mph)
            "wind_gust": {
                "light": 8,          # 0-8 mph: Light gusts
                "moderate": 15,      # 8-15 mph: Moderate gusts
                "strong": 25,        # 15-25 mph: Strong gusts
                "severe": 35         # 25+ mph: Severe gusts
            },
            # Temperature thresholds (°F)
            "temperature": {
                "cold": 40,          # Below 40°F: Cold
                "cool": 50,          # 40-50°F: Cool
                "comfortable": 75,   # 50-75°F: Comfortable
                "warm": 85,          # 75-85°F: Warm
                "hot": 95            # 85+°F: Hot
            },
            # Pressure thresholds (inches Hg)
            "pressure": {
                "very_low": 29.50,   # Below 29.50: Very low (excellent)
                "low": 29.80,        # 29.50-29.80: Low (good)
                "normal": 30.20,     # 29.80-30.20: Normal
                "high": 30.50        # 30.20+: High
            },
            # Moon phase values (0-1)
            "moon_phase": {
                "new_moon": 0.0,     # 0.0: New moon
                "waxing_crescent": 0.25,  # 0.0-0.25: Waxing crescent
                "first_quarter": 0.5,     # 0.25-0.5: First quarter
                "waxing_gibbous": 0.75,   # 0.5-0.75: Waxing gibbous
                "full_moon": 1.0,         # 0.75-1.0: Full moon
                "waning_gibbous": 0.75,   # 0.5-0.75: Waning gibbous
                "last_quarter": 0.5,      # 0.25-0.5: Last quarter
                "waning_crescent": 0.25   # 0.0-0.25: Waning crescent
            }
        }
    
    def analyze_fishing_conditions(self, weather_data: Dict) -> Dict:
        """
        Analyze fishing conditions based on all available weather factors
        
        Args:
            weather_data: Dictionary containing weather data from API
            
        Returns:
            Dictionary with fishing analysis results
        """
        # Extract weather data
        wind_speed = weather_data.get('wind_speed', 0)
        wind_gust = weather_data.get('wind_gust', 0)
        wind_deg = weather_data.get('wind_deg', 0)
        temp_day = weather_data.get('temp', {}).get('day', 0)
        pressure_hpa = weather_data.get('pressure', 1013.25)
        pressure_in = pressure_hpa * 0.02953  # Convert to inches Hg
        moon_phase = weather_data.get('moon_phase', 0)
        weather_main = weather_data.get('weather', [{}])[0].get('main', 'Clear')
        weather_description = weather_data.get('weather', [{}])[0].get('description', 'clear sky')
        clouds = weather_data.get('clouds', 0)
        
        # Analyze each factor
        wind_analysis = self._analyze_wind(wind_speed, wind_gust, wind_deg)
        temp_analysis = self._analyze_temperature(temp_day)
        weather_analysis = self._analyze_weather_conditions(weather_main, weather_description, clouds)
        pressure_analysis = self._analyze_pressure(pressure_in)
        moon_analysis = self._analyze_moon_phase(moon_phase)
        
        # Calculate overall fishing score (0-100)
        overall_score = self._calculate_overall_score(
            wind_analysis, temp_analysis, weather_analysis, 
            pressure_analysis, moon_analysis
        )
        
        # Determine fishing rating
        numeric_rating, rating_description = self._determine_fishing_rating(overall_score)
        
        # Generate detailed analysis
        analysis = {
            'overall_score': overall_score,
            'fishing_rating': numeric_rating,
            'fishing_base': numeric_rating,
            'rating_description': rating_description,
            'wind_analysis': wind_analysis,
            'temperature_analysis': temp_analysis,
            'weather_analysis': weather_analysis,
            'pressure_analysis': pressure_analysis,
            'moon_analysis': moon_analysis,
            'recommendations': self._generate_recommendations(
                wind_analysis, temp_analysis, weather_analysis,
                pressure_analysis, moon_analysis
            ),
            'detailed_summary': self._generate_detailed_summary(
                wind_analysis, temp_analysis, weather_analysis,
                pressure_analysis, moon_analysis, overall_score
            )
        }
        
        return analysis
    
    def _analyze_wind(self, wind_speed: float, wind_gust: float, wind_deg: float) -> Dict:
        """Analyze wind conditions (most important factor)"""
        wind_scores = self.thresholds['wind_speed']
        gust_scores = self.thresholds['wind_gust']
        
        # Wind speed analysis - Based on trolling requirements
        if wind_speed <= wind_scores['excellent']:
            wind_rating = "Excellent"
            wind_score = 100
            wind_description = f"EXCELLENT wind conditions ({wind_speed:.1f} mph) - Perfect for trolling"
        elif wind_speed <= wind_scores['great']:
            wind_rating = "Great"
            wind_score = 85
            wind_description = f"GOOD wind conditions ({wind_speed:.1f} mph) - Very fishable"
        elif wind_speed <= wind_scores['good']:
            wind_rating = "Good"
            wind_score = 65
            wind_description = f"FAIR wind conditions ({wind_speed:.1f} mph) - Manageable but challenging"
        elif wind_speed <= wind_scores['moderate']:
            wind_rating = "Moderate"
            wind_score = 35
            wind_description = f"TOUGH wind conditions ({wind_speed:.1f} mph) - Difficult for trolling"
        elif wind_speed <= wind_scores['challenging']:
            wind_rating = "Challenging"
            wind_score = 10
            wind_description = f"HARD NO - Wind too strong ({wind_speed:.1f} mph) - Not recommended"
        elif wind_speed <= wind_scores['difficult']:
            wind_rating = "Difficult"
            wind_score = 5
            wind_description = f"VERY DIFFICULT winds ({wind_speed:.1f} mph) - Stay home"
        else:
            wind_rating = "Dangerous"
            wind_score = 0
            wind_description = f"DANGEROUS winds ({wind_speed:.1f} mph) - Stay home"
        
        # Wind gust analysis
        if wind_gust <= gust_scores['light']:
            gust_rating = "Light"
            gust_score = 100
            gust_description = f"Light gusts ({wind_gust:.1f} mph)"
        elif wind_gust <= gust_scores['moderate']:
            gust_rating = "Moderate"
            gust_score = 75
            gust_description = f"Moderate gusts ({wind_gust:.1f} mph)"
        elif wind_gust <= gust_scores['strong']:
            gust_rating = "Strong"
            gust_score = 40
            gust_description = f"Strong gusts ({wind_gust:.1f} mph)"
        else:
            gust_rating = "Severe"
            gust_score = 0
            gust_description = f"Severe gusts ({wind_gust:.1f} mph)"
        
        # Wind direction analysis
        wind_direction = self._get_wind_direction(wind_deg)
        
        return {
            'speed': wind_speed,
            'gust': wind_gust,
            'direction': wind_direction,
            'speed_rating': wind_rating,
            'gust_rating': gust_rating,
            'speed_score': wind_score,
            'gust_score': gust_score,
            'speed_description': wind_description,
            'gust_description': gust_description,
            'direction_description': f"Wind from {wind_direction}",
            'overall_wind_score': (wind_score * 0.7 + gust_score * 0.3)  # Weight speed more than gusts
        }
    
    def _analyze_temperature(self, temp_day: float) -> Dict:
        """Analyze temperature conditions"""
        temp_scores = self.thresholds['temperature']
        
        if temp_day < temp_scores['cold']:
            temp_rating = "Cold"
            temp_score = 30
            temp_description = f"Cold temperature ({temp_day:.1f}°F) - Bundle up"
        elif temp_day < temp_scores['cool']:
            temp_rating = "Cool"
            temp_score = 60
            temp_description = f"Cool temperature ({temp_day:.1f}°F) - Dress warmly"
        elif temp_day < temp_scores['comfortable']:
            temp_rating = "Comfortable"
            temp_score = 100
            temp_description = f"Comfortable temperature ({temp_day:.1f}°F) - Perfect"
        elif temp_day < temp_scores['warm']:
            temp_rating = "Warm"
            temp_score = 80
            temp_description = f"Warm temperature ({temp_day:.1f}°F) - Stay hydrated"
        elif temp_day < temp_scores['hot']:
            temp_rating = "Hot"
            temp_score = 50
            temp_description = f"Hot temperature ({temp_day:.1f}°F) - Early morning fishing"
        else:
            temp_rating = "Very Hot"
            temp_score = 20
            temp_description = f"Very hot temperature ({temp_day:.1f}°F) - Avoid midday"
        
        return {
            'temperature': temp_day,
            'rating': temp_rating,
            'score': temp_score,
            'description': temp_description
        }
    
    def _analyze_weather_conditions(self, weather_main: str, weather_description: str, clouds: int) -> Dict:
        """Analyze weather conditions (clear/overcast/rain)"""
        weather_main = weather_main.lower()
        weather_description = weather_description.lower()
        
        # Determine weather type
        if 'clear' in weather_main or 'clear' in weather_description:
            weather_type = "Clear"
            weather_score = 70
            weather_description_text = "Clear skies - Good visibility"
        elif 'cloud' in weather_main or 'cloud' in weather_description:
            if clouds > 80:
                weather_type = "Overcast"
                weather_score = 90
                weather_description_text = "Overcast skies - Excellent fishing conditions"
            else:
                weather_type = "Partly Cloudy"
                weather_score = 80
                weather_description_text = "Partly cloudy - Good fishing conditions"
        elif 'rain' in weather_main or 'rain' in weather_description or 'drizzle' in weather_description:
            weather_type = "Rain"
            weather_score = 40
            weather_description_text = "Rainy conditions - Less enjoyable but fishable"
        elif 'snow' in weather_main or 'snow' in weather_description:
            weather_type = "Snow"
            weather_score = 20
            weather_description_text = "Snowy conditions - Challenging"
        elif 'storm' in weather_main or 'thunder' in weather_description:
            weather_type = "Storm"
            weather_score = 0
            weather_description_text = "Stormy conditions - Stay home"
        else:
            weather_type = "Mixed"
            weather_score = 60
            weather_description_text = f"Mixed conditions - {weather_description}"
        
        return {
            'type': weather_type,
            'description': weather_description,
            'clouds': clouds,
            'score': weather_score,
            'description_text': weather_description_text
        }
    
    def _analyze_pressure(self, pressure_in: float) -> Dict:
        """Analyze pressure conditions (low pressure improves fishing)"""
        pressure_scores = self.thresholds['pressure']
        
        if pressure_in < pressure_scores['very_low']:
            pressure_rating = "Very Low"
            pressure_score = 100
            pressure_description = f"Very low pressure ({pressure_in:.2f} inHg) - Excellent fishing"
        elif pressure_in < pressure_scores['low']:
            pressure_rating = "Low"
            pressure_score = 85
            pressure_description = f"Low pressure ({pressure_in:.2f} inHg) - Good fishing"
        elif pressure_in < pressure_scores['normal']:
            pressure_rating = "Normal"
            pressure_score = 60
            pressure_description = f"Normal pressure ({pressure_in:.2f} inHg) - Average fishing"
        else:
            pressure_rating = "High"
            pressure_score = 30
            pressure_description = f"High pressure ({pressure_in:.2f} inHg) - Poorer fishing"
        
        return {
            'pressure': pressure_in,
            'rating': pressure_rating,
            'score': pressure_score,
            'description': pressure_description
        }
    
    def _analyze_moon_phase(self, moon_phase: float) -> Dict:
        """Analyze moon phase (full moon is better)"""
        # Convert moon phase to a score (0-100)
        # Full moon (1.0) = 100, New moon (0.0) = 50, Quarter moons = 75
        if moon_phase >= 0.875 or moon_phase <= 0.125:  # Full moon range
            moon_rating = "Full Moon"
            moon_score = 100
            moon_description = "Full moon - Excellent fishing conditions"
        elif 0.375 <= moon_phase <= 0.625:  # Quarter moons
            moon_rating = "Quarter Moon"
            moon_score = 75
            moon_description = "Quarter moon - Good fishing conditions"
        else:  # Crescent moons
            moon_rating = "Crescent Moon"
            moon_score = 60
            moon_description = "Crescent moon - Average fishing conditions"
        
        return {
            'phase': moon_phase,
            'rating': moon_rating,
            'score': moon_score,
            'description': moon_description
        }
    
    def _get_wind_direction(self, wind_deg: float) -> str:
        """Convert wind degrees to cardinal direction"""
        directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                     'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        index = round(wind_deg / 22.5) % 16
        return directions[index]
    
    def _calculate_overall_score(self, wind_analysis: Dict, temp_analysis: Dict, 
                                weather_analysis: Dict, pressure_analysis: Dict, 
                                moon_analysis: Dict) -> float:
        """Calculate overall fishing score (0-100)"""
        # Weight factors by importance - Wind speed heavily weighted for trolling
        weights = {
            'wind': 0.60,      # Wind speed is CRITICAL for trolling (60%)
            'temperature': 0.15,  # Secondary factor (15%)
            'weather': 0.10,   # Weather conditions (10%)
            'pressure': 0.10,  # Pressure (10%)
            'moon': 0.05      # Moon phase (5%)
        }
        
        overall_score = (
            wind_analysis['overall_wind_score'] * weights['wind'] +
            temp_analysis['score'] * weights['temperature'] +
            weather_analysis['score'] * weights['weather'] +
            pressure_analysis['score'] * weights['pressure'] +
            moon_analysis['score'] * weights['moon']
        )
        
        return round(overall_score, 1)
    
    def _determine_fishing_rating(self, overall_score: float) -> Tuple[int, str]:
        """Determine fishing rating based on overall score - returns (numeric_rating, description)"""
        if overall_score >= 90:
            return (10, "Perfect conditions for trolling")
        elif overall_score >= 80:
            return (9, "Excellent conditions for fishing")
        elif overall_score >= 70:
            return (8, "Great conditions for fishing")
        elif overall_score >= 60:
            return (7, "Good conditions for fishing")
        elif overall_score >= 50:
            return (6, "Fair conditions for fishing")
        elif overall_score >= 40:
            return (5, "Moderate conditions - some challenges")
        elif overall_score >= 30:
            return (4, "Poor conditions - significant challenges")
        elif overall_score >= 20:
            return (3, "Difficult conditions - high winds/weather")
        elif overall_score >= 10:
            return (2, "Very difficult conditions - extreme weather")
        else:
            return (1, "Stay home - dangerous conditions")
    
    def _generate_recommendations(self, wind_analysis: Dict, temp_analysis: Dict,
                                 weather_analysis: Dict, pressure_analysis: Dict,
                                 moon_analysis: Dict) -> List[str]:
        """Generate fishing recommendations based on conditions"""
        recommendations = []
        
        # Wind recommendations
        if wind_analysis['speed_score'] < 40:
            recommendations.append("Consider fishing in sheltered areas")
        if wind_analysis['gust_score'] < 50:
            recommendations.append("Be prepared for gusty conditions")
        
        # Temperature recommendations
        if temp_analysis['score'] < 50:
            recommendations.append("Dress warmly and bring hot drinks")
        elif temp_analysis['score'] > 80:
            recommendations.append("Fish early morning or evening to avoid heat")
        
        # Weather recommendations
        if weather_analysis['score'] < 50:
            recommendations.append("Bring rain gear and waterproof equipment")
        
        # Pressure recommendations
        if pressure_analysis['score'] > 80:
            recommendations.append("Low pressure - fish are likely more active")
        
        # Moon recommendations
        if moon_analysis['score'] > 80:
            recommendations.append("Full moon conditions - excellent night fishing")
        
        return recommendations
    
    def _generate_detailed_summary(self, wind_analysis: Dict, temp_analysis: Dict,
                                  weather_analysis: Dict, pressure_analysis: Dict,
                                  moon_analysis: Dict, overall_score: float) -> str:
        """Generate a detailed summary of fishing conditions"""
        summary_parts = []
        
        # Wind summary
        summary_parts.append(f"Wind: {wind_analysis['speed_description']}")
        if wind_analysis['gust_score'] < 80:
            summary_parts.append(f"Gusts: {wind_analysis['gust_description']}")
        
        # Temperature summary
        summary_parts.append(f"Temperature: {temp_analysis['description']}")
        
        # Weather summary
        summary_parts.append(f"Weather: {weather_analysis['description_text']}")
        
        # Pressure summary
        if pressure_analysis['score'] > 70:
            summary_parts.append(f"Pressure: {pressure_analysis['description']}")
        
        # Moon summary
        if moon_analysis['score'] > 70:
            summary_parts.append(f"Moon: {moon_analysis['description']}")
        
        return " | ".join(summary_parts)
