from langgraph.graph import StateGraph, END

from models.review import ReviewState
from agents.static_analyzer import static_analyzer_agent
from agents.security_analyzer import security_analyzer_agent


def review_start(state: ReviewState):
    print(f"Starting review: {state['review_id']}")

    return {
        "status": "running"
    }


def build_review_graph():
    graph = StateGraph(ReviewState)

    graph.set_entry_point("review_start")

    graph.add_node("review_start", review_start)
    graph.add_node("static_analyzer", static_analyzer_agent)
    graph.add_node("security_analyzer", security_analyzer_agent)

    graph.add_edge("review_start", "static_analyzer")
    graph.add_edge("static_analyzer", "security_analyzer")
    graph.add_edge("security_analyzer", END)

    return graph.compile()