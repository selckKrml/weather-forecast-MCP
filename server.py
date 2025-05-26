# server.py
from mcp.server.fastmcp import FastMCP
from app import getliveTemp # app.py dosyasındaki getliveTemp fonksiyonunu import ediyoruz

# FastMCP sunucusunu başlatın
# "weather-forecast-mcp" sunucunuzun Smithery.ai'de görünecek adıdır.
mcp = FastMCP("weather-forecast-mcp")

@mcp.tool()
async def get_live_temp(latitude: float, longitude: float) -> dict:
    """
    Belirtilen enlem ve boylama göre canlı sıcaklık verilerini döndürür.
    Bu, Smithery.ai'deki 'Tools' sekmesinde görüntülenecek fonksiyondur.
    """
    # app.py'den gelen getliveTemp fonksiyonunu çağırın.
    # getliveTemp senkron (async değil) olduğu için 'await' kullanmanıza gerek yok.
    result = getliveTemp(latitude, longitude)

    # FastMCP'ye geri dönen sonucu döndür
    return result

if __name__ == "__main__":
    # FastMCP sunucusunu başlatın.
    # 'transport="stdio"' parametresi, Smithery.ai'nin arka planda sunucunuzla stdin/stdout üzerinden iletişim kurması içindir.
    mcp.run(transport="stdio")