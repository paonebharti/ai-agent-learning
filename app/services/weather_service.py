import httpx
import os

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city: str) -> str:
        try:
            response = httpx.get(
                self.base_url,
                params={
                    "q": city,
                    "appid": self.api_key,
                    "units": "metric"
                },
                timeout=5
            )
            response.raise_for_status()
            data = response.json()

            weather = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]

            return (
                f"The weather in {city} is {weather}. "
                f"Temperature: {temp}°C, feels like {feels_like}°C, "
                f"humidity: {humidity}%."
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return f"City '{city}' not found."
            raise

        except Exception as e:
            return f"Could not fetch weather: {str(e)}"
