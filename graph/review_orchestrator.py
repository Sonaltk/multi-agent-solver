from langgraph.graph import StateGraph, END

from models.review import ReviewState


def review_start(state: ReviewState):
    print(f"Starting review: {state["review_id"]}")

    return {
        "status": "running"
    }


def build_review_graph():
    graph = StateGraph(ReviewState)

    graph.set_entry_point("review_start")

    graph.add_node("review_start", review_start)

    graph.add_edge("review_start", END)

    return graph.compile()