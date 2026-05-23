# graph/state.py

from typing import TypedDict, Optional


class AgentState(TypedDict):
    """
    This is the shared memory of the entire multi-agent pipeline.
    Every agent reads from this and writes back to this.
    Think of it as a baton passed between runners in a relay race.
    """

    issue: str                     # The GitHub issue text (the starting input)
    code_context: Optional[str]    # Code read by Agent 01 (Code Reader)
    plan: Optional[str]            # Implementation plan by Agent 02 (Planner)
    patch: Optional[str]           # Code changes written by Agent 03 (Code Writer)
    tests: Optional[str]           # Tests written by Agent 04 (Test Writer)
    pr_url: Optional[str]          # PR link created by Agent 05 (PR Opener)