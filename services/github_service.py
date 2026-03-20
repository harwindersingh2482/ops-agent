import requests
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def parse_repo(repo_input: str):
    repo_input = repo_input.strip().replace("https://github.com/", "").replace("http://github.com/", "")
    repo_input = repo_input.strip("/")
    parts = repo_input.split("/")
    if len(parts) >= 2:
        return parts[0], parts[1]
    return None, None

def get_open_issues(repo_input: str, limit: int = 20):
    owner, repo = parse_repo(repo_input)
    if not owner or not repo:
        return {"error": "Invalid repo format. Use: owner/repo or full GitHub URL"}

    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    params = {"state": "open", "per_page": limit, "sort": "created", "direction": "desc"}

    res = requests.get(url, headers=HEADERS, params=params)

    if res.status_code == 404:
        return {"error": f"Repo not found: {owner}/{repo}"}
    if res.status_code != 200:
        return {"error": f"GitHub API error: {res.status_code}"}

    issues = res.json()
    # Filter out pull requests
    issues = [i for i in issues if "pull_request" not in i]

    return {
        "repo": f"{owner}/{repo}",
        "count": len(issues),
        "issues": [
            {
                "number": i["number"],
                "title": i["title"],
                "body": (i["body"] or "")[:300],
                "labels": [l["name"] for l in i["labels"]],
                "created_at": i["created_at"][:10],
                "url": i["html_url"]
            }
            for i in issues
        ]
    }

def get_repo_info(repo_input: str):
    owner, repo = parse_repo(repo_input)
    if not owner or not repo:
        return {"error": "Invalid repo format"}

    url = f"https://api.github.com/repos/{owner}/{repo}"
    res = requests.get(url, headers=HEADERS)

    if res.status_code != 200:
        return {"error": f"Repo not found: {owner}/{repo}"}

    r = res.json()
    return {
        "name": r["full_name"],
        "description": r["description"],
        "stars": r["stargazers_count"],
        "forks": r["forks_count"],
        "open_issues": r["open_issues_count"],
        "language": r["language"],
        "url": r["html_url"]
    }
