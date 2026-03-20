from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.groq_service import chat_with_groq

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    response = chat_with_groq(request.message)
    return ChatResponse(response=response)
