import os

from dotenv import load_dotenv
from github import Github
from fastapi import HTTPException
from models.review import ReviewState
from agents.static_analyzer import parse_pr_diff

load_dotenv()

def get_github_client():
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        raise RuntimeError("GITHUB_TOKEN is not set")

    return Github(token)


def parse_pr_url(url: str):
    parts = url.strip().rstrip("/").split("/")

    if len(parts) < 5 or parts[-2] != "pull":
        raise ValueError(
            "Invalid GitHub PR URL. Expected: "
            "https://github.com/owner/repo/pull/123"
        )

    owner = parts[-4]
    repo = parts[-3]
    pr_number = int(parts[-1])

    return owner, repo, pr_number


def fetch_pull_request(url: str):
    try:
        owner, repo, pr_number = parse_pr_url(url)
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub PR URL. Expected: "
                   "https://github.com/owner/repo/pull/123"
        )

    github = get_github_client()

    try:
        repository = github.get_repo(f"{owner}/{repo}")
        pull_request = repository.get_pull(pr_number)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch GitHub PR: {str(e)}"
        )

    files = []

    for file in pull_request.get_files():
        files.append({
            "path": file.filename,
            "status": file.status,
            "additions": file.additions,
            "deletions": file.deletions,
            "changes": file.changes,
            "patch": file.patch,
        })

    return {
        "repository": f"{owner}/{repo}",
        "pr_number": pull_request.number,
        "title": pull_request.title,
        "description": pull_request.body or "",
        "base_sha": pull_request.base.sha,
        "head_sha": pull_request.head.sha,
        "changed_files": [file["path"] for file in files],
        "files": files,
        "url": pull_request.html_url,
    }




def build_review_state(pr_data: dict) -> ReviewState:
    parsed_diffs = parse_pr_diff(pr_data)
    

    return {
        "review_id": f"{pr_data['repository']}#PR-{pr_data['pr_number']}",

        "repository": pr_data["repository"],
        "pr_number": pr_data["pr_number"],

        "base_sha": pr_data["base_sha"],
        "head_sha": pr_data["head_sha"],

        "pr_title": pr_data["title"],
        "pr_description": pr_data["description"],

        "changed_files": pr_data["changed_files"],
        "diffs": {
            diff["file"]: diff
            for diff in parsed_diffs
        },

        "repository_context": {},

        "static_findings": [],
        "security_findings": [],
        "style_findings": [],
        "architecture_findings": [],

        "merged_findings": [],

        "review_summary": "",

        "status": "pending",
    }