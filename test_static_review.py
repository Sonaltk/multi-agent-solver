from tools.github_review import fetch_pull_request, build_review_state
from tools.repository_workspace import pr_workspace
from agents.static_analyzer import static_analyzer_agent


PR_URL = "https://github.com/FelisCatus/SwitchyOmega/pull/2342"


# 1. Fetch the PR
pr = fetch_pull_request(PR_URL)

# 2. Build our ReviewState
state = build_review_state(pr)

# 3. Create temporary workspace
with pr_workspace(
    pr["repository"],
    pr["pr_number"],
) as workspace:

    # Give the analyzer access to the checked-out PR code
    state["repository_context"]["workspace"] = workspace

    # 4. Run static analysis
    result = static_analyzer_agent(state)

    # 5. Display findings
    print("\n===== STATIC ANALYSIS =====")
    print("Total findings:", len(result["static_findings"]))

    for finding in result["static_findings"]:
        print("\n", finding)