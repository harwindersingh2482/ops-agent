import requests
import os
from dotenv import load_dotenv

load_dotenv()

TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_BOARD_ID = os.getenv("TRELLO_BOARD_ID")

def get_list_id(list_name: str = "Backlog") -> str:
    try:
        url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/lists"
        params = {"key": TRELLO_API_KEY, "token": TRELLO_TOKEN}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        lists = response.json()
        for lst in lists:
            if lst["name"].lower() == list_name.lower():
                return lst["id"]
        return lists[0]["id"]
    except Exception as e:
        raise Exception(f"Trello list error: {str(e)}")

def create_trello_card(title: str, priority: str = "medium", description: str = "") -> dict:
    try:
        list_id = get_list_id("Backlog")
        priority_labels = {"high": "🔴 HIGH", "medium": "🟡 MEDIUM", "low": "🟢 LOW"}
        label = priority_labels.get(priority.lower(), "🟡 MEDIUM")
        url = "https://api.trello.com/1/cards"
        params = {
            "key": TRELLO_API_KEY,
            "token": TRELLO_TOKEN,
            "idList": list_id,
            "name": f"[{label}] {title}",
            "desc": description or f"Task created by OpsAgent\nPriority: {priority.upper()}"
        }
        response = requests.post(url, params=params, timeout=10)
        response.raise_for_status()
        card = response.json()
        return {
            "id": card.get("id"),
            "title": card.get("name"),
            "url": card.get("shortUrl"),
            "status": "created"
        }
    except Exception as e:
        raise Exception(f"Trello card error: {str(e)}")

def move_card(card_name: str, target_list: str) -> dict:
    try:
        # Get all cards
        url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/cards"
        params = {"key": TRELLO_API_KEY, "token": TRELLO_TOKEN}
        response = requests.get(url, params=params)
        cards = response.json()

        # Find matching card
        card = next((c for c in cards if card_name.lower() in c["name"].lower()), None)
        if not card:
            return {"error": "Card not found"}

        # Get target list ID
        list_id = get_list_id(target_list)

        # Move card
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

    except Exception as e:
        raise Exception(f"Trello move error: {str(e)}")
