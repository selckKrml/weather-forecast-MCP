# app.py
import requests
import os

# API anahtarınızı bir ortam değişkeninden almaya çalışın.
# Eğer ortam değişkeni ayarlanmamışsa, geçici olarak doğrudan buraya yazabilirsiniz
# ANCAK ÜRETİM ORTAMINDA BU KULLANIM GÜVENLİ DEĞİLDİR!
API_KEY = os.getenv("WEATHER_API_KEY", "d2c6107fdaf140df8e094237252605") # Lütfen BURAYI KENDİ API ANAHTARINIZLA DEĞİŞTİRİN!
BASE_URL = "http://api.weatherapi.com/v1/current.json"

def getliveTemp(latitude: float, longitude: float) -> dict:
    """
    Belirtilen enlem ve boylama göre canlı sıcaklık verilerini çeker.
    WeatherAPI.com'dan güncel hava durumu bilgisini alır.
    """
    if not API_KEY or API_KEY == "YOUR_WEATHERAPI_API_KEY_HERE":
        return {"error": "API Anahtarı ayarlanmadı. Lütfen app.py dosyasını güncelleyin veya WEATHER_API_KEY ortam değişkenini ayarlayın."}

    params = {
        "key": API_KEY,
        "q": f"{latitude},{longitude}",
        "aqi": "no" # Hava kalitesi indeksini dahil etme
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10) # 10 saniye zaman aşımı ekle
        response.raise_for_status() # HTTP hataları için istisna fırlat (4xx veya 5xx durum kodları)

        data = response.json()

        # Yanıtta beklenen anahtarların varlığını kontrol et
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
        # Özellikle 401 (Unauthorized) veya 403 (Forbidden) hataları API anahtarı sorununa işaret edebilir.
        if e.response.status_code in [401, 403]:
            return {"error": f"API Anahtarı hatası veya erişim reddedildi: {e.response.status_code} - {e.response.text}. Lütfen API anahtarınızın doğru olduğundan ve geçerli olduğundan emin olun."}
        return {"error": f"WeatherAPI.com'dan HTTP hatası alındı: {e.response.status_code} - {e.response.text}"}
    except requests.exceptions.RequestException as e:
        # Diğer tüm istek hatalarını yakala
        return {"error": f"Bir istek hatası oluştu: {e}"}
    except ValueError:
        return {"error": "WeatherAPI.com yanıtı geçerli bir JSON formatında değil."}
    except Exception as e:
        # Diğer tüm beklenmeyen hataları yakala
        return {"error": f"Beklenmeyen bir hata oluştu: {e}"}