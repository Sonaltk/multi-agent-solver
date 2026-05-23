# api.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()

from github import Github
import os
from graph.orchestrator import build_graph

# ── Initialize FastAPI app ──────────────────────────────────
app = FastAPI(
    title="Multi-Agent GitHub Issue Solver",
    description="Paste a GitHub issue URL and let 5 AI agents analyze and solve it.",
    version="1.0.0"
)

# ── Request model ───────────────────────────────────────────
class IssueRequest(BaseModel):
    github_issue_url: str

# ── Response model ──────────────────────────────────────────
class IssueResponse(BaseModel):
    repo: str
    issue_number: int
    issue_title: str
    issue_url: str
    code_context: str
    plan: str
    patch: str
    tests: str
    pr_description: str

# ── Helper: fetch issue from GitHub ─────────────────────────
def fetch_issue(url: str):
    parts = url.strip().rstrip("/").split("/")
    try:
        owner = parts[-4]
        repo  = parts[-3]
        issue_number = int(parts[-1])
    except (IndexError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub issue URL. Expected: https://github.com/owner/repo/issues/42"
        )

    g = Github(os.getenv("GITHUB_TOKEN"))
    try:
        gh_repo = g.get_repo(f"{owner}/{repo}")
        issue = gh_repo.get_issue(issue_number)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not fetch issue: {str(e)}")

    return {
        "number": issue.number,
        "title": issue.title,
        "body": issue.body or "No description provided.",
        "repo": f"{owner}/{repo}",
        "url": issue.html_url,
    }

# ── Health check endpoint ────────────────────────────────────
@app.get("/")
def root():
    return {"status": "running", "message": "Multi-Agent Issue Solver is live!"}

# ── Main endpoint ────────────────────────────────────────────
@app.post("/solve", response_model=IssueResponse)
def solve_issue(request: IssueRequest):
    # Step 1 - Fetch issue from GitHub
    issue = fetch_issue(request.github_issue_url)

    # Step 2 - Build initial state
    initial_state = {
        "issue": f"Repo: {issue['repo']}\nIssue #{issue['number']}: {issue['title']}\n\n{issue['body']}",
        "code_context": None,
        "plan": None,
        "patch": None,
        "tests": None,
        "pr_url": None,
    }

    # Step 3 - Run the multi-agent pipeline
    graph = build_graph()
    result = graph.invoke(initial_state)

    # Step 4 - Return structured response
    return IssueResponse(
        repo=issue["repo"],
        issue_number=issue["number"],
        issue_title=issue["title"],
        issue_url=issue["url"],
        code_context=result["code_context"],
        plan=result["plan"],
        patch=result["patch"],
        tests=result["tests"],
        pr_description=result["pr_url"]
    )
