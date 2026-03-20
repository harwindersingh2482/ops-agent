from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.groq_service import route_with_groq, chat_with_groq
from services.trello_service import create_trello_card, move_card
from utils.memory import set_last_task, get_last_task, set_options, get_options, clear_options
from utils.logger import add_log, get_logs

router = APIRouter()

class RouteRequest(BaseModel):
    message: str

@router.post("/route")
def route(request: RouteRequest):
    message = request.message.strip().lower()

    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        # 🔥 HANDLE NUMBER OR SELECT
        if message.isdigit() or message.startswith("select"):
            try:
                index = int(message.split()[-1]) - 1
                options = get_options()

                if options and 0 <= index < len(options):
                    selected_task = options[index]
                    clear_options()

                    result = move_card(selected_task, "Done")

                    if result.get("status") == "moved":
                        add_log(f"Moved task: {selected_task} → Done")

                    return {
                        "intent": "update_task",
                        "result": result,
                        "logs": get_logs()
                    }
                else:
                    return {
                        "intent": "update_task",
                        "result": {
                            "status": "error",
                            "message": "Invalid selection"
                        },
                        "logs": get_logs()
                    }
            except:
                return {
                    "intent": "update_task",
                    "result": {
                        "status": "error",
                        "message": "Use: 1, 2 or 'select 1'"
                    },
                    "logs": get_logs()
                }

        # CHECK FOR NOTION INTENT
        if any(word in message for word in ["notion", "note", "log", "save to notion", "add to notion"]):
            from services.notion_service import create_notion_page
            title = request.message.replace("add to notion", "").replace("save to notion", "").replace("note:", "").replace("notion:", "").strip()
            if not title:
                title = "OpsAgent Note"
            result = create_notion_page(title=title, content=request.message)
            add_log(f"Created Notion page: {title}")
            return {"intent": "notion", "result": result, "logs": get_logs()}

        # CHECK FOR GITHUB INTENT
        if any(word in message for word in ["github", "repo", "issues", "repository"]):
            import re
            repo_match = re.search(r"github\.com/[w.-]+/[w.-]+|[w.-]+/[w.-]+", request.message)
            repo = repo_match.group(0) if repo_match else None
            if repo:
                from routers.github import analyze_issues, GithubAnalyzeRequest
                create = any(w in message for w in ["create", "task", "trello", "add"])
                result = analyze_issues(GithubAnalyzeRequest(repo=repo, create_tasks=create))
                add_log(f"GitHub analysis: {repo}")
                return {"intent": "github_analyze", "result": result, "logs": get_logs()}

        # NORMAL FLOW
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
            target = routed.get("target_list", "Backlog")

            result = move_card(task_name, target)

            if result.get("status") == "multiple_found":
                set_options(result.get("options"))

            elif result.get("status") == "moved":
                add_log(f"Moved task: {result.get('title')} → {target}")

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

# Import github analyze at top level
from services.github_service import get_open_issues
