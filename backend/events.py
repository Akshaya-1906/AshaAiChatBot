import requests
import os
from dotenv import load_dotenv

load_dotenv()

EVENTBRITE_TOKEN = os.getenv("EVENTBRITE_API_TOKEN")

def get_events(location="India", keyword="women empowerment"):
    url = "https://www.eventbriteapi.com/v3/events/search/"
    headers = {
        "Authorization": f"Bearer {EVENTBRITE_TOKEN}"
    }
    params = {
        "q": keyword,
        "location.address": location,
        "location.within": "100km",
        "sort_by": "date",
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        events = []
        for event in data.get("events", [])[:5]:  # Limit to 5 events
            events.append({
                "name": event.get("name", {}).get("text", "Untitled Event"),
                "description": event.get("description", {}).get("text", "No description available"),
                "start": event.get("start", {}).get("local", "Date not specified"),
                "url": event.get("url", "#"),
            })
        return events

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            return [{"error": "Too many requests. Please try again later."}]
        return [{"error": f"API request failed: {str(e)}"}]
    except Exception as e:
        return [{"error": f"An unexpected error occurred: {str(e)}"}]