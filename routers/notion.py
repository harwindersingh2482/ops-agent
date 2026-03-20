from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.notion_service import (
    create_notion_page,
    get_notion_pages,
    find_notion_page,
    update_notion_page,
    delete_notion_page
)
from utils.logger import add_log, get_logs

router = APIRouter()

class NotionCreateRequest(BaseModel):
    title: str
    content: str = ""

class NotionUpdateRequest(BaseModel):
    title: str
    new_title: str = None
    content: str = None

class NotionDeleteRequest(BaseModel):
    title: str

@router.post("/notion/create")
def create_page(request: NotionCreateRequest):
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

@router.patch("/notion/update")
def update_page(request: NotionUpdateRequest):
    page = find_notion_page(request.title)
    if not page:
        raise HTTPException(status_code=404, detail=f"Page not found: {request.title}")
    result = update_notion_page(page["id"], title=request.new_title, content=request.content)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    add_log(f"Updated Notion page: {request.title}")
    return {**result, "logs": get_logs()}

@router.delete("/notion/delete")
def delete_page(request: NotionDeleteRequest):
    page = find_notion_page(request.title)
    if not page:
        raise HTTPException(status_code=404, detail=f"Page not found: {request.title}")
    result = delete_notion_page(page["id"])
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    add_log(f"Deleted Notion page: {request.title}")
    return {**result, "title": request.title, "logs": get_logs()}
