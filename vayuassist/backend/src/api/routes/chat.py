import asyncio
import logging
import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from src.services.chat_service import ChatService
from src.utils.rate_limit import check_rate_limit

router = APIRouter()
chat_service = ChatService()
logger = logging.getLogger(__name__)

CHAT_TIMEOUT_SECONDS = 15.0

class ChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=128)
    message: str = Field(..., min_length=1, max_length=2_000)
    language: str = Field(default="en", min_length=2, max_length=10)
    is_voice: bool = False

@router.post("/message")
async def handle_message(req: ChatRequest):
    start = time.time()
    allowed, retry_after = check_rate_limit(req.user_id)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again shortly.",
            headers={"Retry-After": str(retry_after)},
        )

    try:
        result = await asyncio.wait_for(
            chat_service.handle_message(
                user_id=req.user_id,
                message=req.message,
                language=req.language,
                is_voice=req.is_voice,
            ),
            timeout=CHAT_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        logger.warning("Chat request timed out", extra={"user_id": req.user_id})
        result = {
            "response": "Request timed out. Please try again.",
            "intent": "error",
            "escalation_flag": False,
        }
    except Exception:
        logger.exception("Chat request failed", extra={"user_id": req.user_id})
        result = {
            "response": "An error occurred. Please try again.",
            "intent": "error",
            "escalation_flag": False,
        }

    result["latency_ms"] = int((time.time() - start) * 1000)
    return result
