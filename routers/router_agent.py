from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.groq_service import route_with_groq, chat_with_groq
from services.trello_service import create_trello_card

router = APIRouter()

class RouteRequest(BaseModel):
    message: str

@router.post("/route")
def route(request: RouteRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    try:
        routed = route_with_groq(request.message)
        intent = routed.get("intent")

        if intent == "create_task":
            try:
                title = routed.get("title", "Untitled Task")
                priority = routed.get("priority", "medium")
                card = create_trello_card(title=title, priority=priority)
                return {
                    "intent": "create_task",
                    "action_taken": "trello_card_created",
                    "task": card,
                    "confidence": routed.get("confidence"),
                    "raw_routing": routed
                }
            except Exception as e:
                raise HTTPException(status_code=502, detail=f"Trello error: {str(e)}")

        elif intent == "analyze":
            try:
                analysis = chat_with_groq(
                    request.message,
                    system_prompt="You are an operations analyst. Analyze the given data or situation and return concise, actionable insights."
                )
                return {
                    "intent": "analyze",
                    "action_taken": "analysis_completed",
                    "analysis": analysis,
                    "confidence": routed.get("confidence"),
                    "raw_routing": routed
                }
            except Exception as e:
                raise HTTPException(status_code=502, detail=f"Analysis error: {str(e)}")

        else:
            try:
                response = chat_with_groq(request.message)
                return {
                    "intent": "chat",
                    "action_taken": "chat_response",
                    "response": response,
                    "confidence": routed.get("confidence"),
                    "raw_routing": routed
                }
            except Exception as e:
                raise HTTPException(status_code=502, detail=f"Chat error: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Routing failed: {str(e)}")
