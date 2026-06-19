from fastapi import FastAPI
from pydantic import BaseModel

from app.services.llm_client import generate_llm_answer

app = FastAPI(
    title="AI Operations Assistant",
    description="Pet project for AI implementation in business workflows",
    version="0.2.0"
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    user_message: str
    answer: str
    mode: str


@app.get("/")
def home():
    return {
        "message": "AI Operations Assistant is running",
        "status": "ok",
        "version": "0.2.0"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer = generate_llm_answer(request.message)

    return ChatResponse(
        user_message=request.message,
        answer=answer,
        mode="llm_or_mock"
    )
