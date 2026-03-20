from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.groq_service import route_with_groq, chat_with_groq
from services.trello_service import create_trello_card, move_card
from utils.memory import set_last_task, get_last_task

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
            title = routed.get("title", "Untitled Task")
            priority = routed.get("priority", "medium")

            card = create_trello_card(title=title, priority=priority)

            # 🔥 SAVE MEMORY
            set_last_task(title)

            return {
                "intent": "create_task",
                "action_taken": "trello_card_created",
                "task": card
            }

        # UPDATE TASK
        elif intent == "update_task":

            task_name = routed.get("title")

            # 🔥 IF NO TASK → USE MEMORY
            if not task_name:
                task_name = get_last_task()

            result = move_card(
                card_name=task_name,
                target_list=routed.get("target_list", "Backlog")
            )

            return {
                "intent": "update_task",
                "action_taken": "task_moved",
                "result": result
            }

        # ANALYZE
        elif intent == "analyze":
            return {
                "intent": "analyze",
                "analysis": chat_with_groq(request.message)
            }

        # CHAT
        else:
            return {
                "intent": "chat",
                "response": chat_with_groq(request.message)
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
