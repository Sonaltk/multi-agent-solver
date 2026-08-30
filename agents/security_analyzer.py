# agents/security_analyzer.py

import json
import subprocess
from pathlib import Path

from models.review import Finding
from tools.finding_classifier import classify_finding


def run_bandit(
    workspace: str,
    changed_files: list[str],
    changed_lines_by_file: dict[str, list[int]] | None = None,
) -> list[Finding]:
    """
    Run Bandit against the Python files changed by a PR and convert
    its results into our common Finding model, using the same
    "only report on changed lines" filtering as the static analyzer.
    """

    python_files = [
        file
        for file in changed_files
        if file.endswith(".py")
    ]

    if not python_files:
        return []

    result = subprocess.run(
        [
            "bandit",
            "-f",
            "json",
            *python_files,
        ],
        cwd=workspace,
        capture_output=True,
        text=True,
    )

    # Bandit returns exit code 1 when it finds issues.
    # That is not an execution failure for us.
    if result.returncode not in (0, 1):
        raise RuntimeError(
            f"Bandit failed: {result.stderr}"
        )

    if not result.stdout.strip():
        return []

    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(
            f"Bandit returned invalid JSON: {result.stderr}"
        )

    findings = []

    for issue in report.get("results", []):
        # Bandit prefixes filenames with "./" when run from the
        # workspace root — normalize so it matches changed_files paths.
        relative_path = issue["filename"].removeprefix("./")

        line = issue["line_number"]

        changed_lines = (
            changed_lines_by_file or {}
        ).get(relative_path)

        if changed_lines is not None and line not in changed_lines:
            continue

        # Bandit's own severity is used as a fallback for any rule
        # we haven't explicitly overridden in the classifier.
        bandit_severity = issue["issue_severity"]  # LOW / MEDIUM / HIGH

        severity, category = classify_finding(
            issue["test_id"],
            "bandit",
            fallback_severity=bandit_severity,
            fallback_category="security",
        )

        # Bandit's confidence (LOW/MEDIUM/HIGH) maps to our 0-1 float.
        confidence_map = {"HIGH": 0.9, "MEDIUM": 0.6, "LOW": 0.3}
        confidence = confidence_map.get(
            issue.get("issue_confidence", "MEDIUM"), 0.6
        )

        findings.append(
            Finding(
                severity=severity,
                category=category,
                file_path=relative_path,
                line_start=line,
                line_end=issue.get("line_range", [line])[-1],
                title=f"{issue['test_id']} {issue['test_name']}",
                description=issue["issue_text"],
                suggestion=(
                    f"See {issue['more_info']}"
                    if issue.get("more_info")
                    else "Review and correct this issue."
                ),
                confidence=confidence,
            )
        )

    return findings


def security_analyzer_agent(state: dict) -> dict:
    """
    Run security analysis against the files changed by the PR
    and populate state["security_findings"].
    """

    changed_files = state["changed_files"]

    changed_lines_by_file = {
        file_path: diff["changed_lines"]
        for file_path, diff in state["diffs"].items()
    }

    workspace = state["repository_context"]["workspace"]

    findings = run_bandit(
        workspace,
        changed_files,
        changed_lines_by_file,
    )

    state["security_findings"] = findings

    return state