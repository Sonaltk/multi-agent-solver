# agents/test_writer.py

from langchain_groq import ChatGroq
from graph.state import AgentState

llm = ChatGroq(model="llama-3.3-70b-versatile")


def test_writer_agent(state: AgentState) -> AgentState:
    """
    Agent 04 - Test Writer

    Job: Take the code patch from Agent 03 and write
    proper unit tests for it.
    """

    print(">>> Agent 04: Test Writer running...")

    issue = state["issue"]
    patch = state["patch"]

    prompt = f"""
    You are a senior software engineer writing unit tests.

    GitHub Issue:
    {issue}

    Code Patch (from Code Writer agent):
    {patch}

    Your job:
    1. Write comprehensive unit tests for the code patch above
    2. Cover happy path, edge cases, and failure scenarios
    3. Use Python's unittest framework
    4. Add clear comments explaining what each test checks

    Format your response as:
    ### File: test_<filename>.py
```python
    <test code here>
```
    """

    response = llm.invoke(prompt)

    print(">>> Agent 04: Done. Tests written.\n")

    return {**state, "tests": response.content}
