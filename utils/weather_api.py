import requests
import os
from datetime import datetime

class WeatherAPI:
    def __init__(self):
        self.api_key = os.getenv("WEATHERAPI_KEY", "<YOUR-API-KEY>")
        self.base_url = "http://api.weatherapi.com/v1"

    def get_current_weather(self, location, units="Celsius"):
        """Fetch current weather data for a location"""
        try:
            url = f"{self.base_url}/current.json"
            params = {"key": self.api_key, "q": location, "aqi": "no"}
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            temp = data["current"]["temp_c"] if units == "Celsius" else data["current"]["temp_f"]
            wind_speed = data["current"]["wind_kph"] if units == "Celsius" else data["current"]["wind_mph"]

            return {
                "temp": round(temp, 1),
                "feels_like": round(
                    data["current"]["feelslike_c"] if units == "Celsius" else data["current"]["feelslike_f"], 1
                ),
                "humidity": data["current"]["humidity"],
                "pressure": data["current"]["pressure_mb"],
                "wind_speed": wind_speed,
                "wind_deg": data["current"]["wind_degree"],
                "description": data["current"]["condition"]["text"],
                "icon": data["current"]["condition"]["icon"],
                "uv": data["current"].get("uv", 0),
                "vis_km": data["current"].get("vis_km", 0),
                "cloud": data["current"].get("cloud", 0),
                "coord": {
                    "lat": data["location"]["lat"],
                    "lon": data["location"]["lon"],
                },
                "location_name": data["location"]["name"],
                "country": data["location"]["country"],
                "localtime": data["location"].get("localtime", ""),
            }
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch current weather: {str(e)}")

    def get_forecast(self, location, units="Celsius"):
        """Fetch 5-day forecast data with daily summaries and hourly detail."""
        try:
            url = f"{self.base_url}/forecast.json"
            params = {"key": self.api_key, "q": location, "days": 5, "aqi": "no"}
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            hourly_data = []
            daily_summary = []

            for day in data["forecast"]["forecastday"]:
                d = day["day"]
                daily_summary.append({
                    "date": day["date"],
                    "max_temp": d["maxtemp_c"] if units == "Celsius" else d["maxtemp_f"],
                    "min_temp": d["mintemp_c"] if units == "Celsius" else d["mintemp_f"],
                    "avg_temp": d["avgtemp_c"] if units == "Celsius" else d["avgtemp_f"],
                    "avg_humidity": d["avghumidity"],
                    "max_wind": d["maxwind_kph"] if units == "Celsius" else d["maxwind_mph"],
                    "total_precip": d["totalprecip_mm"] if units == "Celsius" else d["totalprecip_in"],
                    "chance_of_rain": d.get("daily_chance_of_rain", 0),
                    "condition": d["condition"]["text"],
                    "icon": d["condition"]["icon"],
                    "uv": d.get("uv", 0),
                    "sunrise": day["astro"]["sunrise"],
                    "sunset": day["astro"]["sunset"],
                })

                for hour in day["hour"]:
                    temp = hour["temp_c"] if units == "Celsius" else hour["temp_f"]
                    wind_speed = hour["wind_kph"] if units == "Celsius" else hour["wind_mph"]
                    hourly_data.append({
                        "datetime": datetime.fromtimestamp(hour["time_epoch"]),
                        "date": day["date"],
                        "temp": temp,
                        "feels_like": hour["feelslike_c"] if units == "Celsius" else hour["feelslike_f"],
                        "humidity": hour["humidity"],
                        "precipitation": hour["chance_of_rain"],
                        "wind_speed": wind_speed,
                        "wind_deg": hour["wind_degree"],
                        "cloud": hour.get("cloud", 0),
                        "uv": hour.get("uv", 0),
                        "condition": hour["condition"]["text"],
                    })

            return {"hourly": hourly_data, "daily": daily_summary}
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch forecast data: {str(e)}")
