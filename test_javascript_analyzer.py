from tools.github_review import fetch_pull_request
from tools.repository_workspace import pr_workspace
from agents.javascript_analyzer import run_eslint
from pathlib import Path


PR_URL = "https://github.com/FelisCatus/SwitchyOmega/pull/2342"
#PR_URL="https://github.com/arvids-unavailable/openGym/pull/20"


pr = fetch_pull_request(PR_URL)

changed_lines_by_file = {
    file["path"]: []
    for file in pr["files"]
}

for file in pr["files"]:
    patch = file.get("patch")

    if not patch:
        continue

    # We'll use the changed lines already produced
    # by our PR diff parser.
    from agents.static_analyzer import extract_changed_lines

    changed_lines_by_file[file["path"]] = extract_changed_lines(
        patch
    )


with pr_workspace(
    pr["repository"],
    pr["pr_number"],
) as workspace:

    print("Workspace:", workspace)
    print(
            "ESLint configs:",
            list(Path(workspace).glob("eslint.config.*"))
        )

    findings = run_eslint(
        workspace,
        pr["changed_files"],
        changed_lines_by_file,
    )

    print("\n===== JAVASCRIPT ANALYSIS =====")
    print("Total findings:", len(findings))

    for finding in findings:
        print(finding)