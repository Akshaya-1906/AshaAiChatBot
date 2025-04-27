from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import DateTime

from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Read database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)  # <-- Added
    user_input = Column(String, index=True)
    bot_response = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create the table
Base.metadata.create_all(bind=engine)

def cleanup_old_messages(db_session, days_old=30):
    cutoff_date = datetime.utcnow() - timedelta(days=days_old)
    db_session.query(Message).filter(Message.created_at < cutoff_date).delete()
    db_session.commit()
