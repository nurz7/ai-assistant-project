from fastapi import APIRouter, HTTPException, status

from app.models.schemas import ChatRequest, ChatResponse
from app.services.chat_service import process_chat
from app.services.llm_client import LLMConfigurationError, LLMProviderError

router = APIRouter(tags=["chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        status.HTTP_502_BAD_GATEWAY: {"description": "LLM provider request failed"},
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "LLM provider is not configured"
        },
    },
)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        return await process_chat(request.message)
    except LLMConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error
    except LLMProviderError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The language model provider is temporarily unavailable.",
        ) from error
