from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # User context for personalization
    family_size = Column(String, default=None)
    location = Column(String, default=None)
    region = Column(String, default="Maharashtra")  # Default region
    health_conditions = Column(String, default=None)  # JSON string

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    user_message = Column(String)
    assistant_response = Column(String)
    intent = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
