from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="AI Operations Assistant",
    description="Pet project for AI implementation in business workflows",
    version="0.1.0"
)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {
        "message": "AI Operations Assistant is running",
        "status": "ok"
    }


@app.post("/chat")
def chat(request: ChatRequest):
    return {
        "user_message": request.message,
        "answer": "This is a placeholder AI response. Later this endpoint will use RAG, SQL tools and reports."
    }
