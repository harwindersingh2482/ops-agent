import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def create_notion_page(title: str, content: str = "", page_id: str = None):
    parent_id = page_id or NOTION_PAGE_ID
    url = "https://api.notion.com/v1/pages"

    body = {
        "parent": {"page_id": parent_id},
        "properties": {
            "title": {
                "title": [{"text": {"content": title}}]
            }
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": content}}]
                }
            }
        ] if content else []
    }

    res = requests.post(url, headers=HEADERS, json=body)

    if res.status_code != 200:
        return {"error": f"Notion API error: {res.status_code} — {res.text}"}

    page = res.json()
    return {
        "status": "created",
        "title": title,
        "url": page.get("url"),
        "id": page.get("id")
    }

def get_notion_pages():
    url = f"https://api.notion.com/v1/blocks/{NOTION_PAGE_ID}/children"
    res = requests.get(url, headers=HEADERS)

    if res.status_code != 200:
        return {"error": f"Notion API error: {res.status_code}"}

    blocks = res.json().get("results", [])
    pages = []

    for b in blocks:
        if b["type"] == "child_page":
            pages.append({
                "id": b["id"],
                "title": b["child_page"]["title"],
            })

    return {"pages": pages, "count": len(pages)}
