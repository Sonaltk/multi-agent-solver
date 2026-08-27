from tools.github_review import fetch_pull_request, build_review_state
from tools.repository_workspace import pr_workspace
from graph.review_orchestrator import build_review_graph


PR_URL = "https://github.com/FelisCatus/SwitchyOmega/pull/2342"


# 1. Fetch PR
pr = fetch_pull_request(PR_URL)

# 2. Build ReviewState
state = build_review_state(pr)

# 3. Create workspace for the entire review
with pr_workspace(
    pr["repository"],
    pr["pr_number"],
) as workspace:

    # Make workspace available to all agents
    state["repository_context"]["workspace"] = workspace

    # 4. Build the LangGraph
    graph = build_review_graph()

    # 5. Run the review pipeline
    result = graph.invoke(state)

    # 6. Display result
    print("\n===== REVIEW COMPLETE =====")
    print("Status:", result["status"])
    print("Static findings:", len(result["static_findings"]))

    for finding in result["static_findings"]:
        print("\n", finding)