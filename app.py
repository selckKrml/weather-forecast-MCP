import requests

API_KEY = "api key"
BASE_URL = "http://api.weatherapi.com/v1/current.json"

def get_weather_by_location(latitude, longitude):
    params = {
        "key": API_KEY,
        "q": f"{latitude},{longitude}",
        "aqi": "no"
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        temp = data["current"]["temp_c"]
        return {"temperature": temp}
    else:
        return {"error": "Failed to fetch weather data"}
