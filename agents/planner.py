# agents/planner.py

from langchain_groq import ChatGroq
from graph.state import AgentState

llm = ChatGroq(model="llama-3.3-70b-versatile")


def planner_agent(state: AgentState) -> AgentState:
    """
    Agent 02 - Planner

    Job: Take the code context from Agent 01 and create a
    clear step-by-step plan to fix the issue.
    """

    print(">>> Agent 02: Planner running...")

    issue = state["issue"]
    code_context = state["code_context"]

    prompt = f"""
    You are a senior software engineer creating an implementation plan.

    GitHub Issue:
    {issue}

    Code Context (from Code Reader agent):
    {code_context}

    Your job:
    1. Create a clear step-by-step plan to fix this issue
    2. For each step, mention which file needs to be changed and what change is needed
    3. Keep it concise and actionable

    This plan will be handed to a Code Writer agent who will implement it.
    """

    response = llm.invoke(prompt)

    print(">>> Agent 02: Done. Plan created.\n")

    return {**state, "plan": response.content}
