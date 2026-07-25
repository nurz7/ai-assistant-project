from time import perf_counter

from fastapi import APIRouter, HTTPException, status

from app.core.observability import (
    create_run_id,
    log_chat_completed,
    log_chat_failed,
)
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
    run_id = create_run_id()
    started_at = perf_counter()
    try:
        response = await process_chat(request.message)
    except LLMConfigurationError as error:
        log_chat_failed(
            run_id=run_id,
            duration_ms=_duration_ms(started_at),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_type=type(error).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error
    except LLMProviderError as error:
        log_chat_failed(
            run_id=run_id,
            duration_ms=_duration_ms(started_at),
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_type=type(error).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The language model provider is temporarily unavailable.",
        ) from error

    log_chat_completed(
        run_id=run_id,
        duration_ms=_duration_ms(started_at),
        response=response,
    )
    return response


def _duration_ms(started_at: float) -> float:
    return round((perf_counter() - started_at) * 1_000, 2)
