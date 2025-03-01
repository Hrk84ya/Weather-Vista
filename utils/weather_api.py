import requests
import os
from datetime import datetime

class WeatherAPI:
    def __init__(self):
        self.api_key = os.getenv("WEATHERAPI_KEY", "<YOUR-API-KEY>")
        self.base_url = "http://api.weatherapi.com/v1"

    def get_current_weather(self, location, units="metric"):
        """Fetch current weather data for a location"""
        try:
            url = f"{self.base_url}/current.json"
            params = {
                "key": self.api_key,
                "q": location,
                "aqi": "no"  # We don't need air quality data for now
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Convert data based on units
            temp = data["current"]["temp_c"] if units == "metric" else data["current"]["temp_f"]
            wind_speed = data["current"]["wind_kph"] if units == "metric" else data["current"]["wind_mph"]

            return {
                "temp": round(temp, 1),
                "feels_like": round(data["current"]["feelslike_c"] if units == "metric" else data["current"]["feelslike_f"], 1),
                "humidity": data["current"]["humidity"],
                "pressure": data["current"]["pressure_mb"],
                "wind_speed": wind_speed,
                "wind_deg": data["current"]["wind_degree"],
                "description": data["current"]["condition"]["text"],
                "icon": data["current"]["condition"]["icon"],
                "coord": {
                    "lat": data["location"]["lat"],
                    "lon": data["location"]["lon"]
                }
            }
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch current weather: {str(e)}")

    def get_forecast(self, location, units="metric"):
        """Fetch 5-day forecast data"""
        try:
            url = f"{self.base_url}/forecast.json"
            params = {
                "key": self.api_key,
                "q": location,
                "days": 5,
                "aqi": "no"
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            forecast_data = []
            for day in data["forecast"]["forecastday"]:
                for hour in day["hour"]:
                    temp = hour["temp_c"] if units == "metric" else hour["temp_f"]
                    wind_speed = hour["wind_kph"] if units == "metric" else hour["wind_mph"]

                    forecast_data.append({
                        "datetime": datetime.fromtimestamp(hour["time_epoch"]),
                        "temp": temp,
                        "humidity": hour["humidity"],
                        "precipitation": hour["chance_of_rain"],
                        "wind_speed": wind_speed,
                        "wind_deg": hour["wind_degree"]
                    })

            return forecast_data
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch forecast data: {str(e)}")