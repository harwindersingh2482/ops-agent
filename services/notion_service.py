import requests
import os
from dotenv import load_dotenv

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
            "title": {"title": [{"text": {"content": title}}]}
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
                "title": b["child_page"]["title"]
            })
    return {"pages": pages, "count": len(pages)}

def find_notion_page(title: str):
    result = get_notion_pages()
    if "error" in result:
        return None
    for page in result["pages"]:
        if title.lower() in page["title"].lower():
            return page
    return None

def update_notion_page(page_id: str, title: str = None, content: str = None):
    if title:
        url = f"https://api.notion.com/v1/pages/{page_id}"
        body = {
            "properties": {
                "title": {"title": [{"text": {"content": title}}]}
            }
        }
        res = requests.patch(url, headers=HEADERS, json=body)
        if res.status_code != 200:
            return {"error": f"Notion update error: {res.status_code} — {res.text}"}

    if content:
        url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        body = {
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"text": {"content": content}}]
                    }
                }
            ]
        }
        res = requests.patch(url, headers=HEADERS, json=body)
        if res.status_code != 200:
            return {"error": f"Notion content update error: {res.status_code} — {res.text}"}

    return {"status": "updated", "id": page_id, "title": title}

def delete_notion_page(page_id: str):
    url = f"https://api.notion.com/v1/blocks/{page_id}"
    res = requests.delete(url, headers=HEADERS)
    if res.status_code != 200:
        return {"error": f"Notion delete error: {res.status_code} — {res.text}"}
    return {"status": "deleted", "id": page_id}
