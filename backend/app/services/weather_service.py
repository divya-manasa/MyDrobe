import requests
from app.config import get_settings

settings = get_settings()

class WeatherService:
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, city: str = None, lat: float = None, lon: float = None) -> dict:
        """Get current weather by city or coordinates"""
        if not self.api_key:
            return {"error": "Weather API key not configured"}
        
        params = {"appid": self.api_key, "units": "metric"}
        
        if city:
            params["q"] = city
        elif lat and lon:
            params["lat"] = lat
            params["lon"] = lon
        else:
            return {"error": "City or coordinates required"}
        
        try:
            response = requests.get(f"{self.base_url}/weather", params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    "temperature": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "humidity": data["main"]["humidity"],
                    "description": data["weather"][0]["description"],
                    "main": data["weather"][0]["main"],
                    "wind_speed": data["wind"]["speed"],
                    "city": data["name"]
                }
            return {"error": f"Weather API error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_forecast(self, city: str = None, lat: float = None, lon: float = None, days: int = 5) -> dict:
        """Get weather forecast"""
        if not self.api_key:
            return {"error": "Weather API key not configured"}
        
        params = {"appid": self.api_key, "units": "metric", "cnt": days * 8}
        
        if city:
            params["q"] = city
        elif lat and lon:
            params["lat"] = lat
            params["lon"] = lon
        else:
            return {"error": "City or coordinates required"}
        
        try:
            response = requests.get(f"{self.base_url}/forecast", params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                forecasts = []
                for item in data["list"]:
                    forecasts.append({
                        "date": item["dt_txt"],
                        "temperature": item["main"]["temp"],
                        "description": item["weather"][0]["description"],
                        "main": item["weather"][0]["main"]
                    })
                return {"forecasts": forecasts, "city": data["city"]["name"]}
            return {"error": f"Weather API error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

weather_service = WeatherService()
