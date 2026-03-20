from fastapi import FastAPI
from dotenv import load_dotenv
from routers import chat, router_agent, ops

load_dotenv()

app = FastAPI(
    title="OpsAgent",
    description="AI-powered operations engine that converts natural language into structured actions.",
    version="1.0.0"
)

app.include_router(chat.router)
app.include_router(router_agent.router)
app.include_router(ops.router)

@app.get("/")
def root():
    return {
        "name": "OpsAgent",
        "version": "1.0.0",
        "status": "online",
        "capabilities": ["chat", "task", "analyze", "route"]
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "1.0.0"
    }
