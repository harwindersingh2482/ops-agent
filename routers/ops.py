from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.groq_service import chat_with_groq

router = APIRouter()

class AnalyzeRequest(BaseModel):
    data: str

@router.post("/analyze")
def analyze(request: AnalyzeRequest):
    if not request.data.strip():
        raise HTTPException(status_code=400, detail="Data cannot be empty")

    system_prompt = """You are an elite operations analyst. 
When given raw business data, fleet reports, sales figures, or any operational information:
- Identify key patterns and anomalies
- Give 3-5 bullet point insights
- Highlight the most critical issue
- Recommend 2-3 concrete next actions
Be concise, direct, and actionable. No fluff."""

    analysis = chat_with_groq(request.data, system_prompt=system_prompt)

    return {
        "status": "analyzed",
        "input_length": len(request.data),
        "analysis": analysis
    }
