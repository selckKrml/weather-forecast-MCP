# server.py
if __name__ == "__main__":
    import sys
    import json
    from app import get_weather_by_location

    for line in sys.stdin:
        try:
            config = json.loads(line)
            lat = config.get("latitude")
            lon = config.get("longitude")
            if lat is None or lon is None:
                print(json.dumps({"error": "latitude and longitude required"}))
                continue

            result = get_weather_by_location(lat, lon)
            print(json.dumps(result))
        except Exception as e:
            print(json.dumps({"error": str(e)}))
