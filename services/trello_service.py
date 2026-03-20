import requests
import os
from dotenv import load_dotenv

load_dotenv()

TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_BOARD_ID = os.getenv("TRELLO_BOARD_ID")


def get_list_id(list_name: str):
    url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/lists"
    params = {"key": TRELLO_API_KEY, "token": TRELLO_TOKEN}
    lists = requests.get(url, params=params).json()

    for lst in lists:
        if lst["name"].lower() == list_name.lower():
            return lst["id"]
    return lists[0]["id"]


# ✅ CREATE TASK (RESTORED)
def create_trello_card(title: str, priority: str = "medium", description: str = ""):
    list_id = get_list_id("Backlog")

    priority_labels = {
        "high": "🔴 HIGH",
        "medium": "🟡 MEDIUM",
        "low": "🟢 LOW"
    }

    label = priority_labels.get(priority.lower(), "🟡 MEDIUM")

    url = "https://api.trello.com/1/cards"
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN,
        "idList": list_id,
        "name": f"[{label}] {title}",
        "desc": description or f"Task created by OpsAgent\nPriority: {priority.upper()}"
    }

    response = requests.post(url, params=params)
    card = response.json()

    return {
        "id": card.get("id"),
        "title": card.get("name"),
        "url": card.get("shortUrl"),
        "status": "created"
    }


# ✅ MOVE SINGLE TASK (WITH MULTI MATCH HANDLING)
def move_card(card_name: str, target_list: str):
    url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/cards"
    params = {"key": TRELLO_API_KEY, "token": TRELLO_TOKEN}
    cards = requests.get(url, params=params).json()

    matches = [c for c in cards if card_name.lower() in c["name"].lower()]

    if not matches:
        return {"status": "not_found"}

    if len(matches) > 1:
        return {
            "status": "multiple_found",
            "options": [c["name"] for c in matches]
        }

    card = matches[0]
    list_id = get_list_id(target_list)

    move_url = f"https://api.trello.com/1/cards/{card['id']}"
    move_params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN,
        "idList": list_id
    }

    requests.put(move_url, params=move_params)

    return {
        "status": "moved",
        "title": card["name"],
        "target_list": target_list
    }


# ✅ MOVE MULTIPLE TASKS
def move_multiple_cards(keyword: str, target_list: str):
    url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/cards"
    params = {"key": TRELLO_API_KEY, "token": TRELLO_TOKEN}
    cards = requests.get(url, params=params).json()

    matched_cards = [c for c in cards if keyword.lower() in c["name"].lower()]

    if not matched_cards:
        return {"message": "No matching cards found"}

    list_id = get_list_id(target_list)

    moved = []
    for card in matched_cards:
        move_url = f"https://api.trello.com/1/cards/{card['id']}"
        move_params = {
            "key": TRELLO_API_KEY,
            "token": TRELLO_TOKEN,
            "idList": list_id
        }
        requests.put(move_url, params=move_params)
        moved.append(card["name"])

    return {
        "moved_count": len(moved),
        "tasks": moved,
        "target_list": target_list
    }
