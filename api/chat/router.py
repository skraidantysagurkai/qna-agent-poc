from typing import Annotated

from fastapi import APIRouter
from fastapi_injector import Injected
from fastapi import HTTPException

from api.chat.chat_service import ChatService
from api.chat.models import ChatRequest
from api.shared.logger import get_logger

LOGGER = get_logger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


@router.post("/")
async def chat_endpoint(
    request: ChatRequest,
    chat_handler: Annotated[ChatService, Injected(ChatService)],
):
    try:
        return await chat_handler.chat(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        LOGGER.info(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
