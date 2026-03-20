from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def chat_with_groq(message: str, system_prompt: str = None) -> str:
    try:
        if not system_prompt:
            system_prompt = "You are OpsAgent, an AI-powered operations assistant. You help businesses automate workflows, manage tasks, and analyze operational data. Be concise, professional, and actionable."
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Groq API error: {str(e)}")

def route_with_groq(message: str) -> dict:
    try:
        system_prompt = """You are an AI operations router.

Your job:
- Understand user intent from their message
- Extract structured data
- Return ONLY valid JSON, nothing else, no explanation, no markdown

Possible intents:
- chat: general question or conversation
- create_task: user wants to create a task or ticket
- update_task: user wants to update or move a task
- analyze: user wants to analyze data or get insights

Output format:
{
  "intent": "chat" or "create_task" or "analyze",
  "title": "task title if intent is create_task, else null",
  "priority": "high, medium, or low if intent is create_task, else null",
  "message": "original message or analysis request",
  "confidence": "high, medium, or low",
  "target_list": "Backlog, In Progress, or Done if update_task"
}"""
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
        )
        raw = response.choices[0].message.content.strip()
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"intent": "chat", "message": message, "confidence": "low"}
    except Exception as e:
        raise Exception(f"Groq routing error: {str(e)}")
