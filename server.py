# server.py
# Bu dosya, FastMCP uygulamasını ve şehir adına göre hava durumu getiren aracı tanımlar.

import os
import requests
# FastMCP ve Tool (büyük T ile) sınıflarını içe aktarıyoruz.
from mcp.server.fastmcp import FastMCP, Tool
from pydantic import Field # Alan doğrulama ve açıklama için kullanılır

# WeatherAPI.com API anahtarını ortam değişkeninden al.
# Güvenlik için anahtarınızı doğrudan koda yazmak yerine ortam değişkeni kullanmak önemlidir.
# Eğer ortam değişkeni ayarlanmamışsa, bir uyarı yazdırılır.
WEATHERAPI_API_KEY = os.getenv("WEATHERAPI_API_KEY")
if not WEATHERAPI_API_KEY:
    print("WARNING: WEATHERAPI_API_KEY environment variable is not set. Weather data fetching will likely fail.")
    print("Please set the WEATHERAPI_API_KEY environment variable before running.")


# FastMCP uygulamasını başlat.
# Bu, Smithery.ai'de görünecek olan MCP servisinizin adını ve açıklamasını tanımlar.
mcp_app = FastMCP(
    title="Weather Data Tool by City", # Başlığı güncelledik
    description="Provides tools for fetching live temperature data for a given city name.", # Açıklamayı güncelledik
    version="1.0.0"
)

# 'get_live_temp' aracını tanımla.
# '@mcp_app.Tool()' dekoratörü, bu fonksiyonu bir MCP aracı olarak kaydeder.
# Bu araç, Smithery.ai'nin "Tools" sekmesinde ve diğer istemcilerde keşfedilebilir olacaktır.
@mcp_app.Tool()
async def get_live_temp(
    # Şehir adını alacak yeni parametre.
    # 'Field' ile açıklama ekleyerek API dokümantasyonunu zenginleştiriyoruz.
    city_name: str = Field(..., description="The name of the city to get weather for, e.g., 'Istanbul', 'London'")
) -> dict:
    """
    Belirtilen şehir adına göre mevcut sıcaklığı (Celsius) ve konum adını döndürür.
    """
    # API anahtarının yapılandırılıp yapılandırılmadığını kontrol et.
    if not WEATHERAPI_API_KEY:
        return {"error": "WeatherAPI API Key is not configured. Please set the WEATHERAPI_API_KEY environment variable."}

    # WeatherAPI.com'un API endpoint'i ve parametreleri.
    # 'q' parametresi hem koordinatları hem de şehir adlarını kabul eder.
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHERAPI_API_KEY}&q={city_name}"

    try:
        # API isteğini gönder.
        response = requests.get(url, timeout=10) # 10 saniye zaman aşımı ekledik
        response.raise_for_status()  # HTTP 4xx veya 5xx hataları için istisna fırlatır.

        # JSON yanıtını ayrıştır.
        data = response.json()

        # Yanıtta beklenen anahtarların (current, temp_c, location, name) varlığını kontrol et.
        if "current" in data and "temp_c" in data["current"] and \
           "location" in data and "name" in data["location"]:
            
            temperature_c = data['current']['temp_c']
            location_name = data['location']['name'] # API'den gelen kesin şehir adı
            
            return {
                "temperature": temperature_c,
                "location": location_name
            }
        else:
            # Beklenmeyen bir JSON yapısı durumunda hata döndür.
            return {"error": f"API yanıtında beklenen hava durumu verisi veya konum bilgisi bulunamadı. Yanıt: {data}"}

    except requests.exceptions.Timeout:
        # İstek zaman aşımına uğradığında hata.
        return {"error": "API isteği zaman aşımına uğradı. WeatherAPI.com'a ulaşılamıyor veya çok yavaş."}
    except requests.exceptions.ConnectionError:
        # Bağlantı hatası durumunda hata.
        return {"error": "WeatherAPI.com'a bağlanırken bir sorun oluştu. İnternet bağlantınızı kontrol edin."}
    except requests.exceptions.HTTPError as e:
        # HTTP hataları (örneğin 401 Unauthorized, 404 Not Found, 1006 No matching location).
        if e.response.status_code == 401 or e.response.status_code == 403:
            return {"error": f"API Anahtarı hatası veya erişim reddedildi: {e.response.status_code}. Lütfen API anahtarınızın doğru ve geçerli olduğundan emin olun."}
        
        # WeatherAPI'nin "No matching location found" hatası (code: 1006)
        try:
            error_data = e.response.json()
            if "error" in error_data and error_data["error"]["code"] == 1006:
                return {"error": f"No matching location found for '{city_name}'. Please check the city name and try again."}
        except ValueError:
            # Yanıt JSON değilse veya farklı bir hata formatıysa
            pass
            
        return {"error": f"WeatherAPI.com'dan HTTP hatası alındı: {e.response.status_code} - {e.response.text}"}
    except ValueError:
        # API yanıtı geçerli bir JSON formatında değilse hata.
        return {"error": "WeatherAPI.com yanıtı geçerli bir JSON formatında değil."}
    except Exception as e:
        # Diğer tüm beklenmeyen hataları yakala.
        return {"error": f"Beklenmeyen bir hata oluştu: {e}"}

# Bu 'if __name__ == "__main__":' bloğu, FastMCP uygulamasının Smithery.ai'de nasıl başlatılacağını belirtir.
# 'transport="stdio"' FastMCP'nin Smithery.ai'nin dahili iletişim mekanizmasını kullanmasını sağlar.
# Yerel test için bu bloğu kullanmak yerine, app.py'yi uvicorn ile çalıştırmak daha yaygındır.
if __name__ == "__main__":
    mcp_app.run(transport="stdio")
