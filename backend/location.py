import requests
import os
from dotenv import load_dotenv

load_dotenv()
IPINFO_TOKEN = os.getenv("IPINFO_TOKEN")

def get_location(ip=""):
    try:
        url = f"https://api.ipgeolocation.io/ipgeo?apiKey={IPINFO_TOKEN}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country"),
            "location": data.get("loc")
        }
    except Exception as e:
        return {"error": str(e)}
