import os
import requests
import asyncio
from fastapi import FastAPI, Request, Cookie
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from backend.chat_memory import get_chat_history, update_chat_history, create_session_id, load_chat_history_from_db
from backend.database import SessionLocal, Message, cleanup_old_messages
from backend.job_listings import get_jooble_jobs, get_remotive_jobs
from backend.events import get_events
from backend.location import get_location
from backend.crypto_utils import encrypt_text, decrypt_text
from backend.intent_classifier import classify_intent
from backend.mistral_client import call_mistral  # ✅ use real AI model here

from collections import defaultdict

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500","http://localhost:5500","http://127.0.0.1:5501","http://localhost:5501","http://127.0.0.1:5502","http://localhost:5502","http://127.0.0.1:5503","http://localhost:5503"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatRequest(BaseModel):
    message: str

# Session trackers
job_session_tracker = defaultdict(lambda: {"keywords": "", "location": "", "offset": 0})

# Nearby fallback for events
NEARBY_DISTRICTS = {
    "Coimbatore": ["Tiruppur", "Erode", "Salem"],
    "Chennai": ["Kanchipuram", "Thiruvallur"],
    "Madurai": ["Dindigul", "Sivaganga"],
    "Bangalore": ["Kolar", "Tumkur", "Mandya"]
}

# --- Utility functions ---
def extract_location_from_message(message: str) -> str:
    locations = [
        "coimbatore", "tiruppur", "erode", "chennai", "madurai", "salem",
        "hyderabad", "bangalore", "mumbai", "pune", "delhi", "noida", "gurgaon", "kolkata", "bombay"
    ]
    for loc in locations:
        if loc in message.lower():
            return loc.capitalize()
    return ""

def extract_job_keyword(message: str) -> str:
    import re
    message = message.lower()
    ignored_words = {"hey", "hi", "hello", "please", "can", "i", "get", "some", "any", "show", "me", "looking", "find", "want", "need", "there", "available", "openings"}
    job_keywords = [
        "software developer", "data analyst", "web developer", "product manager",
        "project manager", "graphic designer", "ui ux designer", "content writer",
        "marketing manager", "software engineer", "full stack developer", "frontend developer",
        "backend developer", "hr manager", "customer support", "sales executive", "qa engineer",
        "python developer", "java developer", "machine learning engineer", "devops engineer",
        "designer", "marketing", "engineer", "data", "analyst", "internship", "remote",
        "frontend", "backend", "fullstack", "manager", "hr", "sales", "qa", "testing"
    ]
    for phrase in job_keywords:
        if phrase in message:
            return phrase
    words = re.findall(r"\b\w+\b", message)
    for word in words:
        if word not in ignored_words and word in job_keywords:
            return word
    if any(x in message for x in ["anything", "opportunities", "openings", "vacancy"]):
        return "jobs"
    return "jobs"

def extract_event_keyword(message: str) -> str:
    message = message.lower()
    multi_word_keywords = ["mentorship program", "career development", "professional networking", "women empowerment"]
    single_keywords = ["mentorship", "career", "networking", "leadership", "training", "session", "growth", "skills"]
    for phrase in multi_word_keywords:
        if phrase in message:
            return phrase
    for word in message.split():
        if word in single_keywords:
            return word
    return "women empowerment"

# --- Main chat route ---

@app.post("/chat")
async def chat(request: Request, body: ChatRequest, session_id: str = Cookie(None)):
    if not session_id:
        session_id = create_session_id()

    db = SessionLocal()
    cleanup_old_messages(db)

    user_message = body.message.lower()
    update_chat_history(session_id, "user", user_message)

    detected_location = get_location(request.client.host).get("city", "India")
    extracted_location = extract_location_from_message(user_message)
    final_location = extracted_location if extracted_location else detected_location

    # Intent detection
    intent_result = classify_intent(user_message)

    # Offensive or bias
    if intent_result["intent"] in ["offensive", "bias"]:
        response_text = intent_result["response"]
        update_chat_history(session_id, "assistant", response_text)
        db.add(Message(session_id=session_id, user_input=encrypt_text(user_message), bot_response=encrypt_text(response_text)))
        db.commit()
        db.close()
        response = JSONResponse({"reply": response_text})
        response.set_cookie(key="session_id", value=session_id, max_age=3600, httponly=True, samesite="lax")
        return response

    # Jobs query
    if any(word in user_message for word in ["job", "jobs", "opening", "openings", "vacancy", "more job", "more openings", "more opportunities"]):
        previous_state = job_session_tracker[session_id]
        is_more_request = any(word in user_message for word in ["more", "next"])

        if is_more_request and previous_state["keywords"]:
            keywords = previous_state["keywords"]
            final_location = previous_state["location"]
            offset = previous_state["offset"] + 5
        else:
            keywords = extract_job_keyword(user_message)
            job_session_tracker[session_id]["keywords"] = keywords
            job_session_tracker[session_id]["location"] = final_location
            offset = 0

        job_session_tracker[session_id]["offset"] = offset

        jooble_jobs = get_jooble_jobs(keywords, final_location)
        remotive_jobs = get_remotive_jobs(keywords)

        jobs = jooble_jobs + remotive_jobs

        if not jobs:
            jooble_jobs = get_jooble_jobs(keywords, "India")
            jobs = jooble_jobs + remotive_jobs

        if not jobs:
            response_text = f"Sorry, I couldn't find job openings for '{keywords}' near {final_location}."
        else:
            response_text = f"🔍 Here are job openings near **{final_location}** for **{keywords}**:\n\n"
            for job in jobs[offset:offset+5]:
                response_text += f"💼 {job['title']} at {job['company']}\n📍 {job['location']}\n🔗 {job['link']}\n\n"
            response_text = response_text.strip()

        update_chat_history(session_id, "assistant", response_text)
        db.add(Message(session_id=session_id, user_input=encrypt_text(user_message), bot_response=encrypt_text(response_text)))
        db.commit()
        db.close()

        response = JSONResponse({"reply": response_text})
        response.set_cookie(key="session_id", value=session_id, max_age=3600, httponly=True, samesite="lax")
        return response

    # Event query
    if "event" in user_message or any(word in user_message for word in ["session", "mentorship", "career", "empowerment", "training", "networking"]):
        event_keyword = extract_event_keyword(user_message)
        keywords_list = [event_keyword, "career development", "mentorship", "professional networking", "women empowerment"]

        events = []
        for keyword in keywords_list:
            events = get_events(final_location, keyword)
            if events and not events[0].get("error"):
                break

        if events:
            response_text = f"🌟 Here are some upcoming **{event_keyword}** events near **{final_location}**:\n\n"
            for event in events[:5]:
                event_name = event.get('name', 'Unknown Event')
                event_start = event.get('start', 'Date not available')
                event_url = event.get('url', '#')

                response_text += f"🎤 {event_name}\n📅 {event_start}\n🔗 {event_url}\n\n"

            response_text = response_text.strip()
        else:
            nearby = NEARBY_DISTRICTS.get(final_location, [])
            if nearby:
                nearby_str = ", ".join(nearby)
                response_text = f"😕 No {event_keyword} events found in {final_location}. Want to check nearby districts like {nearby_str}?"
            else:
                response_text = f"😕 No {event_keyword} events found near {final_location}."

        update_chat_history(session_id, "assistant", response_text)
        db.add(Message(session_id=session_id, user_input=encrypt_text(user_message), bot_response=encrypt_text(response_text)))
        db.commit()
        db.close()

        response = JSONResponse({"reply": response_text})
        response.set_cookie(key="session_id", value=session_id, max_age=3600, httponly=True, samesite="lax")
        return response

    # Fallback to AI model (call mistral/openrouter)
    try:
        structured_history = [{"role": "system", "content": "You are Asha AI, a career companion for career guidance, jobs, mentorships, and events."}]
        history = get_chat_history(session_id)
        for msg in history[-6:]:
            structured_history.append({"role": msg["role"], "content": msg["content"]})
        structured_history.append({"role": "user", "content": body.message})

        ai_reply = call_mistral(structured_history)
    except Exception as e:
        print(f"AI fallback error: {e}")
        ai_reply = "I'm here to guide you! 😊"

    update_chat_history(session_id, "assistant", ai_reply)
    db.add(Message(session_id=session_id, user_input=encrypt_text(user_message), bot_response=encrypt_text(ai_reply)))
    db.commit()
    db.close()

    response = JSONResponse({"reply": ai_reply})
    response.set_cookie(key="session_id", value=session_id, max_age=3600, httponly=True, samesite="lax")
    return response

# Load chat history
@app.get("/history")
async def load_history(session_id: str = Cookie(None)):
    if not session_id:
        session_id = create_session_id()

    chat_history = get_chat_history(session_id)
    if not chat_history:
        past_chats = load_chat_history_from_db(session_id)
        for msg in past_chats:
            update_chat_history(session_id, msg["role"], msg["content"])
        chat_history = get_chat_history(session_id)

    return {"history": chat_history}

# Delete conversation
@app.delete("/delete_conversation")
async def delete_conversation():
    db = SessionLocal()
    db.query(Message).delete()
    db.commit()
    db.close()
    return {"message": "All chat messages cleared."}
