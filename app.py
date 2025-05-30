import requests
import os

API_KEY = ""
BASE_URL = "http://api.weatherapi.com/v1/current.json"

def getliveTemp(city_name: str) -> dict:
    """
    Verilen şehir adına göre canlı sıcaklık verilerini döndürür.
    """
    if not API_KEY:
        return {"error": "API Anahtarı ayarlanmadı. Lütfen API_KEY değerini kontrol edin."}

    params = {
        "key": API_KEY,
        "q": city_name,
        "aqi": "no"
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "current" in data and "temp_c" in data["current"] and "location" in data and "name" in data["location"]:
            current_temp = data["current"]["temp_c"]
            location_name = data["location"]["name"]
            return {"temperature": current_temp, "location": location_name}
        else:
            return {"error": "API yanıtında beklenen hava durumu verisi veya konum bilgisi bulunamadı."}

    except requests.exceptions.Timeout:
        return {"error": "API isteği zaman aşımına uğradı. WeatherAPI.com'a ulaşılamıyor veya çok yavaş."}
    except requests.exceptions.ConnectionError:
        return {"error": "WeatherAPI.com'a bağlanırken bir sorun oluştu. İnternet bağlantınızı kontrol edin."}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code in [401, 403]:
            return {"error": f"API Anahtarı hatası veya erişim reddedildi: {e.response.status_code} - {e.response.text}"}
        return {"error": f"WeatherAPI.com'dan HTTP hatası alındı: {e.response.status_code} - {e.response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Bir istek hatası oluştu: {e}"}
    except ValueError:
        return {"error": "WeatherAPI.com yanıtı geçerli bir JSON formatında değil."}
    except Exception as e:
        return {"error": f"Beklenmeyen bir hata oluştu: {e}"}
