import os
import requests
from typing import Dict, Any


class WeatherTool:
    """Tool for interacting with OpenWeather API"""
    
    def __init__(self):
        self.api_key = os.environ.get("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, city: str, units: str = "metric") -> Dict[str, Any]:

        try:
            url = f"{self.base_url}/weather"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": units
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant information
            weather_info = {
                "city": data.get("name"),
                "country": data.get("sys", {}).get("country"),
                "temperature": data.get("main", {}).get("temp"),
                "feels_like": data.get("main", {}).get("feels_like"),
                "temp_min": data.get("main", {}).get("temp_min"),
                "temp_max": data.get("main", {}).get("temp_max"),
                "humidity": data.get("main", {}).get("humidity"),
                "pressure": data.get("main", {}).get("pressure"),
                "weather": data.get("weather", [{}])[0].get("main"),
                "description": data.get("weather", [{}])[0].get("description"),
                "wind_speed": data.get("wind", {}).get("speed"),
                "clouds": data.get("clouds", {}).get("all"),
                "units": "°C" if units == "metric" else "°F" if units == "imperial" else "K"
            }
            
            return weather_info
        
        except requests.exceptions.RequestException as e:
            return {"error": f"Weather API request failed: {str(e)}"}
    
    def get_weather_forecast(self, city: str, units: str = "metric") -> Dict[str, Any]:

        try:
            url = f"{self.base_url}/forecast"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": units
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract forecast data (API returns 3-hour intervals)
            forecasts = []
            for item in data.get("list", [])[:8]:  # Get next 24 hours (8 x 3-hour intervals)
                forecasts.append({
                    "datetime": item.get("dt_txt"),
                    "temperature": item.get("main", {}).get("temp"),
                    "weather": item.get("weather", [{}])[0].get("main"),
                    "description": item.get("weather", [{}])[0].get("description"),
                    "humidity": item.get("main", {}).get("humidity"),
                    "wind_speed": item.get("wind", {}).get("speed")
                })
            
            return {
                "city": data.get("city", {}).get("name"),
                "country": data.get("city", {}).get("country"),
                "forecasts": forecasts,
                "units": "°C" if units == "metric" else "°F" if units == "imperial" else "K"
            }
        
        except requests.exceptions.RequestException as e:
            return {"error": f"Weather API request failed: {str(e)}"}
    
    def get_weather_by_coordinates(self, lat: float, lon: float, units: str = "metric") -> Dict[str, Any]:

        try:
            url = f"{self.base_url}/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": units
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "location": f"{data.get('name')}, {data.get('sys', {}).get('country')}",
                "temperature": data.get("main", {}).get("temp"),
                "feels_like": data.get("main", {}).get("feels_like"),
                "weather": data.get("weather", [{}])[0].get("main"),
                "description": data.get("weather", [{}])[0].get("description"),
                "humidity": data.get("main", {}).get("humidity"),
                "wind_speed": data.get("wind", {}).get("speed"),
                "units": "°C" if units == "metric" else "°F" if units == "imperial" else "K"
            }
        
        except requests.exceptions.RequestException as e:
            return {"error": f"Weather API request failed: {str(e)}"}