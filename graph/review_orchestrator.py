from langgraph.graph import StateGraph, END

from models.review import ReviewState
from agents.static_analyzer import static_analyzer_agent
from agents.security_analyzer import security_analyzer_agent
from agents.ai_reviewer import ai_reviewer_agent
from agents.finding_merger import finding_merger_agent


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
    graph.add_node("ai_reviewer", ai_reviewer_agent)
    graph.add_node("finding_merger", finding_merger_agent)

    graph.add_edge("review_start", "static_analyzer")
    graph.add_edge("static_analyzer", "security_analyzer")
    graph.add_edge("security_analyzer", "ai_reviewer")
    graph.add_edge("ai_reviewer", "finding_merger")
    graph.add_edge("finding_merger", END)

    return graph.compile()