# agents/code_writer.py

from langchain_groq import ChatGroq
from graph.state import AgentState

llm = ChatGroq(model="llama-3.3-70b-versatile")


def code_writer_agent(state: AgentState) -> AgentState:
    """
    Agent 03 - Code Writer

    Job: Take the plan from Agent 02 and write the actual
    code patch to fix the issue.
    """

    print(">>> Agent 03: Code Writer running...")

    issue = state["issue"]
    code_context = state["code_context"]
    plan = state["plan"]

    prompt = f"""
    You are a senior software engineer writing code to fix a bug.

    GitHub Issue:
    {issue}

    Code Context:
    {code_context}

    Implementation Plan:
    {plan}

    Your job:
    1. Write the actual code changes needed to fix this issue
    2. For each file that needs changing, show the updated code
    3. Use Python as the language
    4. Include comments explaining what each change does

    Format your response as:
    ### File: <filename>
```python
    <code here>
```
    """

    response = llm.invoke(prompt)

    print(">>> Agent 03: Done. Code patch written.\n")

    return {**state, "patch": response.content}
