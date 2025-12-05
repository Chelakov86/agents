import requests

# Using Open-Meteo API - free, no API key required
# https://open-meteo.com/

def get_coordinates(city: str):
    """Get latitude and longitude for a city using Open-Meteo geocoding API."""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    response = requests.get(url)
    if response.status_code != 200:
        return None, None
    data = response.json()
    if not data.get("results"):
        return None, None
    result = data["results"][0]
    return result["latitude"], result["longitude"]


def fetch_weather(lat: float, lon: float):
    """Fetch current weather data from Open-Meteo API."""
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,weather_code"
    )
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch weather data")
    return response.json()


# WMO Weather interpretation codes
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
}


class Weather:
    def __init__(self, data):
        current = data.get("current", {})
        self.temperature = f"{current.get('temperature_2m', 'N/A')}°C"
        self.humidity = f"{current.get('relative_humidity_2m', 'N/A')}%"
        self.pressure = f"{current.get('surface_pressure', 'N/A')} hPa"
        self.wind_speed = f"{current.get('wind_speed_10m', 'N/A')} km/h"
        weather_code = current.get("weather_code", -1)
        self.description = WEATHER_CODES.get(weather_code, "Unknown")

    @classmethod
    def get(cls, location: str):
        lat, lon = get_coordinates(location)
        if lat is None or lon is None:
            return cls({
                "current": {
                    "temperature_2m": "Unknown location",
                    "relative_humidity_2m": "N/A",
                    "surface_pressure": "N/A",
                    "wind_speed_10m": "N/A",
                    "weather_code": -1
                }
            })
        try:
            data = fetch_weather(lat, lon)
            return cls(data)
        except Exception as e:
            return cls({
                "current": {
                    "temperature_2m": f"Error: {e}",
                    "relative_humidity_2m": "N/A",
                    "surface_pressure": "N/A",
                    "wind_speed_10m": "N/A",
                    "weather_code": -1
                }
            })
