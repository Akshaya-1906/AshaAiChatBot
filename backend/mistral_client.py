# mistral_client.py

import requests
import os

OPENROUTER_API_KEY = os.getenv("API_KEY")

def call_mistral(chat_history: list, temperature=0.7) -> str:
    url = os.getenv("API_URL")
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": chat_history,
        "temperature": temperature
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]