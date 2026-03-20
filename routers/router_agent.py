from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.groq_service import route_with_groq, chat_with_groq
from services.trello_service import create_trello_card, move_card

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

        # CREATE TASK
        if intent == "create_task":
            card = create_trello_card(
                title=routed.get("title", "Untitled Task"),
                priority=routed.get("priority", "medium")
            )
            return {
                "intent": "create_task",
                "action_taken": "trello_card_created",
                "task": card
            }

        # UPDATE TASK (NEW 🔥)
        elif intent == "update_task":
            result = move_card(
                card_name=routed.get("title", ""),
                target_list=routed.get("target_list", "Backlog")
            )
            return {
                "intent": "update_task",
                "action_taken": "task_moved",
                "result": result
            }

        # ANALYZE
        elif intent == "analyze":
            analysis = chat_with_groq(request.message)
            return {
                "intent": "analyze",
                "analysis": analysis
            }

        # CHAT
        else:
            response = chat_with_groq(request.message)
            return {
                "intent": "chat",
                "response": response
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
