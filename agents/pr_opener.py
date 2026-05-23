# agents/pr_opener.py

from langchain_groq import ChatGroq
from graph.state import AgentState

llm = ChatGroq(model="llama-3.3-70b-versatile")


def pr_opener_agent(state: AgentState) -> AgentState:
    """
    Agent 05 - PR Opener

    Job: Take everything produced by all agents and generate
    a professional Pull Request description.
    """

    print(">>> Agent 05: PR Opener running...")

    issue = state["issue"]
    plan = state["plan"]
    patch = state["patch"]
    tests = state["tests"]

    prompt = f"""
    You are a senior software engineer opening a Pull Request on GitHub.

    Original Issue:
    {issue}

    Implementation Plan:
    {plan}

    Code Changes:
    {patch}

    Tests Written:
    {tests}

    Your job:
    Write a professional Pull Request description that includes:
    1. **Title**: A clear one-line title for the PR
    2. **Summary**: What problem this PR solves
    3. **Changes Made**: A bullet list of all files changed and why
    4. **Testing**: How the changes were tested
    5. **Checklist**: A standard PR checklist (code reviewed, tests pass, docs updated)

    Make it look like a real GitHub PR description using markdown.
    """

    response = llm.invoke(prompt)

    print(">>> Agent 05: Done. PR description ready.\n")

    # In a real system this would call the GitHub API to open a PR
    # For now we return the PR description as the pr_url field
    return {**state, "pr_url": response.content}
