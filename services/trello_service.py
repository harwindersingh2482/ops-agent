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
