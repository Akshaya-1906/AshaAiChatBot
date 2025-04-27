# AshaAI Chatbot 🤖✨

Your personal career companion for job listings, events, mentorship, and career advice!

---

## 📦 Project Structure

AshaAI_Chatbot/ 
├── backend/ │
 ├── main.py │ 
 ├── chat_memory.py │
 ├── database.py │ 
 ├── crypto_utils.py │ 
 ├── events.py │ 
 ├── intent_classifier.py │ 
 ├── job_listings.py │ 
 ├── location.py │ 
 ├── mistral_client.py │ 
 ├── chatbot.db 
 │ └── .env.template
├── frontend/ │
 ├── index.html │ 
 ├── style.css │ 
 ├── script.js │ 
 ├── logo.png 
└── README.md


---

## ⚙️ Setup Backend (FastAPI)

1. Open terminal inside `/backend/`


2. Create and activate virtual environment:

   python -m venv venv
   source venv/bin/activate  # (Mac/Linux)
   .\venv\Scripts\activate    # (Windows)


3.Install dependencies:

pip install fastapi uvicorn python-dotenv sqlalchemy cryptography requests


4.Create .env file:

Copy .env.template to .env:
cp .env.template
 .env


5.Fill your API keys inside .env:

env
API_KEY="your OpenRouter API key"
API_URL="https://openrouter.ai/api/v1/chat/completions"
DATABASE_URL="sqlite:///chatbot.db"
MODEL_NAME="mistralai/mistral-7b-instruct"
JOOBLE_API_KEY="your Jooble API key"
EVENTBRITE_API_TOKEN="your Eventbrite API token"
IPINFO_TOKEN="your IPInfo API token"


6.Run the FastAPI server:

uvicorn main:app --reload


7.Backend server will run at:

http://127.0.0.1:8000



## 🌐 Setup Frontend

Open /frontend/ folder.
Open index.html directly in your browser.
Make sure backend server is running first.

## 💬 Chatbot Features

🧠 Multi-turn conversation memory
🛡️ Offensive/Bias message detection
💼 Job listings from Jooble and Remotive
🎟️ Events from Eventbrite
🤖 Fallback AI chat using Mistral (OpenRouter)
💬 Load previous chat history on page refresh
🧹 Clear chat history with a button
🍪 Session management via cookies


## 🧠 Important Notes

If chatbot says "⚠️ Failed to connect", check if backend is running.

Keep your .env secret — never upload real keys publicly!

Jooble or Eventbrite APIs may sometimes be rate limited — bot will handle it gracefully.

🚀 Future Upgrades (Optional)
Add user authentication (login/signup)

Add voice-to-text functionality

Deploy backend to free hosting (Render.com / Railway.app)

Improve database for tracking user's career journey

## 🎉 Congratulations!
You now have a full production-ready AI-powered career chatbot! 🚀
with ❤️ Akshaya N E + Mirunalini ❤️ 

