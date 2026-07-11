from fastapi import APIRouter
from pydantic import BaseModel
from src.services.chat_service import ChatService
import time

router = APIRouter()
chat_service = ChatService()

class ChatRequest(BaseModel):
    user_id: str
    message: str
    language: str = "en"
    is_voice: bool = False

@router.post("/message")
async def handle_message(req: ChatRequest):
    start = time.time()
    result = await chat_service.handle_message(
        user_id=req.user_id,
        message=req.message,
        language=req.language,
        is_voice=req.is_voice
    )
    result["latency_ms"] = int((time.time() - start) * 1000)
    return result
