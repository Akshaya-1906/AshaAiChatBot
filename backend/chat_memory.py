# chat_memory.py

from typing import List, Dict
from uuid import uuid4

# In-memory storage for chat history
chat_sessions: Dict[str, List[Dict[str, str]]] = {}

def create_session_id() -> str:
    return str(uuid4())

def get_chat_history(session_id: str) -> List[Dict[str, str]]:
    return chat_sessions.get(session_id, [])

def update_chat_history(session_id: str, role: str, content: str):
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    chat_sessions[session_id].append({"role": role, "content": content})

def reset_chat_history(session_id: str):
    chat_sessions[session_id] = []

# ✅ New function to load from DB
from database import SessionLocal, Message
from crypto_utils import decrypt_text

def load_chat_history_from_db(session_id: str) -> List[Dict[str, str]]:
    db = SessionLocal()
    messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at).all()
    db.close()

    history = []
    for message in messages:
        history.append({"role": "user", "content": decrypt_text(message.user_input)})
        history.append({"role": "assistant", "content": decrypt_text(message.bot_response)})
    
    return history
