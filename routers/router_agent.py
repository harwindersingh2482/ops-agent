from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.groq_service import route_with_groq, chat_with_groq
from services.trello_service import create_trello_card, move_card
from utils.memory import set_last_task, get_last_task
from utils.logger import add_log, get_logs

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
            card = create_trello_card(title=title)

            set_last_task(title)
            add_log(f"Created task: {title}")

            return {
                "intent": "create_task",
                "task": card,
                "logs": get_logs()
            }

        # UPDATE TASK
        elif intent == "update_task":
            task_name = routed.get("title") or get_last_task()

            result = move_card(
                card_name=task_name,
                target_list=routed.get("target_list", "Backlog")
            )

            add_log(f"Moved task: {task_name} → {routed.get('target_list')}")

            return {
                "intent": "update_task",
                "result": result,
                "logs": get_logs()
            }

        # ANALYZE
        elif intent == "analyze":
            analysis = chat_with_groq(request.message)

            add_log("Analyzed business data")

            return {
                "intent": "analyze",
                "analysis": analysis,
                "logs": get_logs()
            }

        # CHAT
        else:
            response = chat_with_groq(request.message)

            add_log("Chat interaction")

            return {
                "intent": "chat",
                "response": response,
                "logs": get_logs()
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
