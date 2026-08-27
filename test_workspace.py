import os

from tools.github_review import fetch_pull_request
from tools.repository_workspace import pr_workspace


pr = fetch_pull_request(
    "https://github.com/FelisCatus/SwitchyOmega/pull/2342"
)

workspace_path = None

with pr_workspace(
    pr["repository"],
    pr["pr_number"],
) as workspace:

    workspace_path = workspace

    print("Workspace:", workspace)
    print("Exists inside:", os.path.exists(workspace))


print("Exists after:", os.path.exists(workspace_path))