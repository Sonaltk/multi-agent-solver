# graph/orchestrator.py

from langgraph.graph import StateGraph, END
from graph.state import AgentState
from agents.code_reader import code_reader_agent  # Real Agent 01
from agents.planner import planner_agent          # Real Agent 02
from agents.code_writer import code_writer_agent  # Real Agent 03
from agents.test_writer import test_writer_agent  # Real Agent 04
from agents.pr_opener import pr_opener_agent      # Real Agent 05

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("code_reader", code_reader_agent)
    graph.add_node("planner", planner_agent)
    graph.add_node("code_writer", code_writer_agent)
    graph.add_node("test_writer", test_writer_agent)
    graph.add_node("pr_opener", pr_opener_agent)
    graph.set_entry_point("code_reader")
    graph.add_edge("code_reader", "planner")
    graph.add_edge("planner", "code_writer")
    graph.add_edge("code_writer", "test_writer")
    graph.add_edge("test_writer", "pr_opener")
    graph.add_edge("pr_opener", END)
    return graph.compile()
