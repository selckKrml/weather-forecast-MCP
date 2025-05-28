from mcp.server.fastmcp import FastMCP
from app import getliveTemp  # getliveTemp fonksiyonunu alıyoruz

mcp = FastMCP("weather-forecast-mcp")

@mcp.tool()
async def get_live_temp(city_name: str) -> dict:
    """
    Verilen şehir adına göre canlı sıcaklık verisini döndürür.
    Bu, Smithery.ai'deki 'Tools' sekmesinde görüntülenecek fonksiyondur.
    """
    return getliveTemp(city_name)

if __name__ == "__main__":
    mcp.run(transport="stdio")
