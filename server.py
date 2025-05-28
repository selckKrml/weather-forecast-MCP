# server.py
import os
import requests
from mcp.server.fastmcp import FastMCP, tool
from pydantic import Field # Daha sağlam veri doğrulaması için

# Smithery.ai'de ortam değişkeni olarak ayarlamanız gereken API anahtarı
WEATHERAPI_API_KEY = os.getenv("WEATHERAPI_API_KEY")
if not WEATHERAPI_API_KEY:
    # Geliştirme ortamında test için uyarı
    print("WARNING: WEATHERAPI_API_KEY environment variable is not set. Weather data fetching will fail.")


# FastMCP uygulamasını başlat
mcp_app = FastMCP(
    title="Weather Data Tool",
    description="Provides tools for fetching live weather data by city name.", # Açıklamayı güncelledik
    version="1.0.0"
)

# get_live_temp aracının adını ve parametrelerini değiştirelim
# Daha açıklayıcı olması için ismini get_city_weather olarak değiştirebiliriz.
# Ancak şimdilik get_live_temp olarak tutalım, sadece parametre değişimi yapalım
@mcp_app.tool()
async def get_live_temp( # Fonksiyon adı aynı kalabilir, sadece parametre değişti
    city_name: str = Field(..., description="The name of the city to get weather for, e.g., 'Istanbul', 'New York'")
) -> dict:
    """
    Retrieves the current temperature (in Celsius) and the exact location name for a given city name.
    """
    if not WEATHERAPI_API_KEY:
        return {"error": "WeatherAPI API Key is not configured."}

    # WeatherAPI'nin "q" parametresi hem koordinat hem de şehir adı alabilir
    # Dolayısıyla doğrudan city_name'i "q" parametresi olarak kullanacağız
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHERAPI_API_KEY}&q={city_name}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTP hataları için istisna fırlatır (4xx veya 5xx)
        data = response.json()

        # API yanıtından sıcaklık ve konum adını al
        temperature_c = data['current']['temp_c']
        location_name = data['location']['name'] # API'den gelen kesin şehir adı
        
        return {
            "temperature": temperature_c,
            "location": location_name # Kullanıcının girdiği isimden farklı olabilir (örn. "İstanbul" girip "Istanbul" gelmesi)
        }
    except requests.exceptions.RequestException as e:
        # Ağ hataları, bağlantı sorunları vb.
        return {"error": f"Failed to connect to weather service or invalid city name: {e}. Please check the city name."}
    except KeyError as e:
        # JSON yanıtında beklenen anahtarların bulunamaması veya şehir bulunamadığında
        # WeatherAPI genellikle {"error": {"code": 1006, "message": "No matching location found."}} döndürür
        if "error" in data and data["error"]["code"] == 1006:
             return {"error": f"No matching location found for '{city_name}'. Please check the city name and try again."}
        return {"error": f"Invalid weather data format from API: Missing key {e}. Response: {data}"}
    except Exception as e:
        # Diğer tüm beklenmeyen hatalar
        return {"error": f"An unexpected error occurred: {e}"}

# Smithery.ai gibi bir MCP platformunda dağıtım için bu kısım önemlidir.
# Yerel test için uvicorn'u doğrudan app.py'den çalıştırmak daha yaygındır.
# if __name__ == "__main__":
#     # Sadece yerel test için:
#     # uvicorn.run(mcp_app, host="0.0.0.0", port=8000)
#     # Smithery.ai'nin FastMCP ile iletişim kurmasını sağlamak için
#     # `mcp_app.run(transport="stdio")` kullanılır.
#     # Bu, Smithery.ai'deki 'server'ın çalıştığı ortamda otomatik olarak çağrılır.
#     mcp_app.run(transport="stdio")