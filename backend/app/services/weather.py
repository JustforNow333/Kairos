from pydantic import BaseModel
import httpx
from ..schemas import WeatherContext

# Open-Meteo free API endpoint. Coordinates set for Ithaca, NY (Cornell).
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
ITHACA_LAT = 42.4440
ITHACA_LON = -76.5019

def fetch_live_weather() -> WeatherContext:
    try:
        response = httpx.get(
            WEATHER_API_URL,
            params={
                "latitude": ITHACA_LAT,
                "longitude": ITHACA_LON,
                "current": ["temperature_2m", "weather_code"],
                "temperature_unit": "fahrenheit",
                "timezone": "America/New_York"
            },
            timeout=5.0
        )
        response.raise_for_status()
        data = response.json()
        current = data.get("current", {})
        temp_f = round(current.get("temperature_2m", 65.0))
        wmo_code = current.get("weather_code", 0)
        
        # WMO Weather interpretation codes (abridged mapping)
        if wmo_code in [0, 1]:
            condition = "clear"
            summary = "Clear Skies"
        elif wmo_code in [2, 3]:
            condition = "cloudy"
            summary = "Partly Cloudy"
        elif wmo_code in [45, 48]:
            condition = "fog"
            summary = "Foggy"
        elif wmo_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
            condition = "rain"
            summary = "Rainy"
        elif wmo_code in [71, 73, 75, 77, 85, 86]:
            condition = "snow"
            summary = "Snowing"
        elif wmo_code in [95, 96, 99]:
            condition = "storm"
            summary = "Thunderstorm"
        else:
            condition = "unknown"
            summary = "Variable"

        return WeatherContext(
            summary=summary,
            condition=condition,
            temperature_f=temp_f,
        )
    except Exception as e:
        print(f"Weather API failed: {e}")
        # Fallback to good weather if API fails
        return WeatherContext(
            summary="Clear Skies",
            condition="clear",
            temperature_f=72.0,
        )
