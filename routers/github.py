from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.github_service import get_open_issues, get_repo_info
from services.groq_service import chat_with_groq
from services.trello_service import create_trello_card
from utils.logger import add_log, get_logs

router = APIRouter()

class GithubRequest(BaseModel):
    repo: str

class GithubAnalyzeRequest(BaseModel):
    repo: str
    create_tasks: bool = False

@router.get("/github/info")
def repo_info(repo: str):
    result = get_repo_info(repo)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.post("/github/issues")
def list_issues(request: GithubRequest):
    result = get_open_issues(request.repo)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    add_log(f"Fetched issues: {result['repo']}")
    return result

@router.post("/github/analyze")
def analyze_issues(request: GithubAnalyzeRequest):
    data = get_open_issues(request.repo, limit=20)

    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])

    if data["count"] == 0:
        return {
            "repo": data["repo"],
            "message": "No open issues found.",
            "tasks_created": []
        }

    issues_text = "\n".join([
        f"#{i['number']}: {i['title']} | Labels: {', '.join(i['labels']) or 'none'} | {i['url']}"
        for i in data["issues"]
    ])

    prompt = f"""You are an expert engineering manager analyzing GitHub issues for: {data['repo']}

Here are the open issues:
{issues_text}

Your job:
1. Pick the TOP 3 most critical issues to fix first
2. For each, explain WHY it's critical in one sentence
3. Suggest priority: high / medium / low

Return in this exact format:
ISSUE #[number] | [title] | Priority: [high/medium/low]
Why: [one sentence reason]
---
ISSUE #[number] | [title] | Priority: [high/medium/low]
Why: [one sentence reason]
---
ISSUE #[number] | [title] | Priority: [high/medium/low]
Why: [one sentence reason]"""

    analysis = chat_with_groq(prompt)
    add_log(f"Analyzed {data['count']} issues from {data['repo']}")

    tasks_created = []

    if request.create_tasks:
        top_issues = data["issues"][:3]
        for issue in top_issues:
            title = f"[GitHub] #{issue['number']} {issue['title']}"
            card = create_trello_card(
                title=title,
                priority="high",
                description=f"GitHub Issue: {issue['url']}\n\n{issue['body']}"
            )
            tasks_created.append(card)
            add_log(f"Created Trello task from GitHub issue #{issue['number']}")

    return {
        "repo": data["repo"],
        "total_issues": data["count"],
        "analysis": analysis,
        "tasks_created": tasks_created,
        "logs": get_logs()
    }
