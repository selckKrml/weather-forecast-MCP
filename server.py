from mcp.server.fastmcp import FastMCP
from app import getliveTemp

mcp = FastMCP("weather-forecast-mcp")

@mcp.tool()
async def get_live_temp(city_name: str) -> dict:
    """
    Verilen şehir adına göre canlı sıcaklık verisini döndürür.
    Bu, Smithery.ai'deki 'Tools' sekmesinde görüntülenecek fonksiyondur.
    """
    result = getliveTemp(city_name)
    return result

if __name__ == "__main__":
    mcp.run(transport="stdio")
