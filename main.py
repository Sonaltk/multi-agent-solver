# main.py

from dotenv import load_dotenv
load_dotenv()

from github import Github
import os
from graph.orchestrator import build_graph

def fetch_issue_from_url(url: str):
    parts = url.strip().rstrip("/").split("/")
    try:
        owner = parts[-4]
        repo  = parts[-3]
        issue_number = int(parts[-1])
    except (IndexError, ValueError):
        print("❌ Invalid GitHub issue URL.")
        print("   Expected format: https://github.com/owner/repo/issues/42")
        exit(1)

    g = Github(os.getenv("GITHUB_TOKEN"))
    print(f"\n🔍 Fetching issue from GitHub: {owner}/{repo} #{issue_number}...\n")

    try:
        gh_repo = g.get_repo(f"{owner}/{repo}")
        issue = gh_repo.get_issue(issue_number)
    except Exception as e:
        print(f"❌ Could not fetch issue: {e}")
        exit(1)

    return {
        "number": issue.number,
        "title": issue.title,
        "body": issue.body or "No description provided.",
        "repo": f"{owner}/{repo}",
        "url": issue.html_url,
    }


# ── Entry point ──────────────────────────────────────────────

print("\n🤖 Multi-Agent GitHub Issue Solver")
print("=" * 40)
url = input("\n👉 Paste a GitHub issue URL: ").strip()

# Fetch the real issue
chosen = fetch_issue_from_url(url)

print(f"✅ Found issue: #{chosen['number']} — {chosen['title']}")
print(f"   Repo: {chosen['repo']}")
print(f"   URL:  {chosen['url']}\n")

# Build initial state
initial_state = {
    "issue": f"Repo: {chosen['repo']}\nIssue #{chosen['number']}: {chosen['title']}\n\n{chosen['body']}",
    "code_context": None,
    "plan": None,
    "patch": None,
    "tests": None,
    "pr_url": None,
}

# Run the pipeline
graph = build_graph()
print("=== Starting Multi-Agent Pipeline ===\n")
result = graph.invoke(initial_state)

# Print everything to terminal
print("\n" + "=" * 60)
print("📋 ISSUE ANALYZED")
print("=" * 60)
print(f"Repo:  {chosen['repo']}")
print(f"Issue: #{chosen['number']} — {chosen['title']}")
print(f"URL:   {chosen['url']}")

print("\n" + "=" * 60)
print("🔍 CODE CONTEXT (Agent 01)")
print("=" * 60)
print(result["code_context"])

print("\n" + "=" * 60)
print("📝 IMPLEMENTATION PLAN (Agent 02)")
print("=" * 60)
print(result["plan"])

print("\n" + "=" * 60)
print("💻 CODE PATCH (Agent 03)")
print("=" * 60)
print(result["patch"])

print("\n" + "=" * 60)
print("🧪 TESTS (Agent 04)")
print("=" * 60)
print(result["tests"])

print("\n" + "=" * 60)
print("🚀 PR DESCRIPTION (Agent 05)")
print("=" * 60)
print(result["pr_url"])

print("\n" + "=" * 60)
print("✅ Pipeline Complete! Copy the PR description above to open a PR.")
print("=" * 60 + "\n")
