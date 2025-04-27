import os
import requests
from dotenv import load_dotenv

# Step 1: Load environment variables
load_dotenv()

# Step 2: Read Jooble API key
JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY")

# Step 3: Define Remotive API URL
REMOTIVE_API_URL = "https://remotive.io/api/remote-jobs"



# Step 4: Function to fetch jobs from Jooble
def get_jooble_jobs(keywords, location="India"):
    url = f"https://jooble.org/api/{JOOBLE_API_KEY}"
    payload = {
        "keywords": keywords,
        "location": location,
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise error for bad status
        data = response.json()
        jobs = [
            {
                "title": job.get("title"),
                "company": job.get("company"),
                "location": job.get("location"),
                "link": job.get("link"),
                "snippet": job.get("snippet"),
            }
            for job in data.get("jobs", [])
        ]
        return jobs
    except Exception as e:
        print(f"Error fetching Jooble jobs: {e}")
        return []

# Step 5: Function to fetch jobs from Remotive
def get_remotive_jobs(category):
    params = {"category": category}
    try:
        response = requests.get(REMOTIVE_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        jobs = [
            {
                "title": job.get("title"),
                "company": job.get("company_name"),
                "location": job.get("candidate_required_location"),
                "link": job.get("url"),
                "description": job.get("description"),
            }
            for job in data.get("jobs", [])
        ]
        return jobs
    except Exception as e:
        print(f"Error fetching Remotive jobs: {e}")
        return []