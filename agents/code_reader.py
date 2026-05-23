# agents/code_reader.py

from langchain_groq import ChatGroq
from graph.state import AgentState

# Initialize the LLM (Groq - Free)
llm = ChatGroq(model="llama-3.3-70b-versatile")


def code_reader_agent(state: AgentState) -> AgentState:
    """
    Agent 01 - Code Reader

    Job: Read the GitHub issue and figure out which parts of the
    codebase are likely relevant to solving it.
    """

    print(">>> Agent 01: Code Reader running...")

    issue = state["issue"]

    prompt = f"""
    You are a senior software engineer analyzing a GitHub issue.

    GitHub Issue:
    {issue}

    Your job:
    1. Identify what part of the codebase is likely causing this issue
    2. List the files or modules that would need to be looked at
    3. Explain what the code in those areas probably does

    Be concise and technical. This output will be passed to a Planner agent.
    """

    response = llm.invoke(prompt)

    print(">>> Agent 01: Done. Code context extracted.\n")

    return {**state, "code_context": response.content}
