from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from src.config.database import get_db
from src.models.models import User, ChatMessage
from src.services.chat_service import ChatService
from src.services.auth_service import decode_token

router = APIRouter(prefix="/chat", tags=["chat"])
chat_service = ChatService()

class ChatMessageRequest(BaseModel):
    message: str
    token: str  # JWT token

class ChatMessageResponse(BaseModel):
    response: str
    intent: str
    escalation: bool

@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    db: Session = Depends(get_db)
):
    """Send chat message and get response"""
    
    # Verify token
    user_id = decode_token(request.token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get user context
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_context = {
        "family_size": user.family_size,
        "location": user.location,
        "region": user.region,
        "health_conditions": user.health_conditions
    }
    
    # Get chat response
    response = await chat_service.handle_message(
        user_id=user_id,
        message=request.message,
        user_context=user_context
    )
    
    # Store in database
    chat_msg = ChatMessage(
        user_id=user_id,
        user_message=request.message,
        assistant_response=response["response"],
        intent=response["intent"]
    )
    db.add(chat_msg)
    db.commit()
    
    return ChatMessageResponse(
        response=response["response"],
        intent=response["intent"],
        escalation=response["escalation"]
    )

@router.get("/history")
async def get_chat_history(token: str, db: Session = Depends(get_db)):
    """Get user's chat history"""
    
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == user_id
    ).order_by(ChatMessage.created_at.desc()).limit(50).all()
    
    return [
        {
            "user_message": m.user_message,
            "assistant_response": m.assistant_response,
            "intent": m.intent,
            "created_at": m.created_at
        }
        for m in messages
    ]
