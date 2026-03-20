from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from routers import chat, router_agent, ops

load_dotenv()

app = FastAPI(
    title="OpsAgent",
    description="AI-powered operations engine that converts natural language into structured actions.",
    version="1.0.0"
)

templates = Jinja2Templates(directory="templates")

app.include_router(chat.router)
app.include_router(router_agent.router)
app.include_router(ops.router)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "1.0.0"
    }
