from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.notion_service import create_notion_page, get_notion_pages
from utils.logger import add_log, get_logs

router = APIRouter()

class NotionRequest(BaseModel):
    title: str
    content: str = ""

@router.post("/notion/create")
def create_page(request: NotionRequest):
    result = create_notion_page(request.title, request.content)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    add_log(f"Created Notion page: {request.title}")
    return {**result, "logs": get_logs()}

@router.get("/notion/pages")
def list_pages():
    result = get_notion_pages()
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
