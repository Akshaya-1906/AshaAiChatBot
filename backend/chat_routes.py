from fastapi import APIRouter, HTTPException, Request, Response, Cookie
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from chat_memory import get_chat_history, update_chat_history, create_session_id
from mistral_client import call_mistral

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat/ai")
def chat_endpoint(chat_req: ChatRequest, session_id: str = Cookie(None)):
    # Step 1: Check if session_id exists in cookies
    if not session_id:
        # If no session_id exists, create one
        session_id = create_session_id()

    # Step 2: Retrieve chat history for the session
    chat_history = get_chat_history(session_id)

    # Step 3: Add the user's message to the history
    update_chat_history(session_id, "user", chat_req.message)

    # Step 4: Get the updated history
    updated_history = get_chat_history(session_id)

    try:
        # Step 5: Call Mistral with the chat history
        bot_reply = call_mistral(updated_history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Step 6: Save the assistant's reply in the chat history
    update_chat_history(session_id, "assistant", bot_reply)

    # Step 7: Return the response with the session ID stored in a cookie
    response = JSONResponse({
        "session_id": session_id,
        "reply": bot_reply
    })

    # Set the session ID cookie with an expiry time (e.g., 1 hour)
    response.set_cookie(key="session_id", value=session_id, max_age=3600, httponly=True, samesite="lax")

    return response