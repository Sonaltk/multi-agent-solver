import re
import json
import subprocess
from pathlib import Path

from models.review import Finding
from tools.language_detector import detect_languages
from tools.finding_classifier import classify_finding
from agents.javascript_analyzer import run_eslint

def extract_changed_lines(patch: str) -> list[int]:
    """
    Extract line numbers added/changed in the new version
    of a file from a unified Git diff.
    """

    changed_lines = []
    current_line = None

    for line in patch.splitlines():

        # Example:
        # @@ -120,6 +120,10 @@
        match = re.match(
            r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@",
            line
        )

        if match:
            current_line = int(match.group(1))
            continue

        if current_line is None:
            continue

        # Added line
        if line.startswith("+") and not line.startswith("+++"):
            changed_lines.append(current_line)
            current_line += 1

        # Deleted line
        elif line.startswith("-") and not line.startswith("---"):
            # Deleted lines don't exist in the new file.
            continue

        # Context line
        else:
            current_line += 1

    return changed_lines

def parse_pr_diff(pr: dict) -> list[dict]:
    """
    Parse all changed files in a pull request.

    Returns one structured dictionary per changed file.
    """

    parsed_files = []

    for file in pr.get("files", []):
        patch = file.get("patch")

        # Some GitHub files may not have a patch
        # (for example, binary files).
        if not patch:
            continue

        changed_lines = extract_changed_lines(patch)

        added_lines = []
        removed_lines = []

        for line in patch.splitlines():

            if line.startswith("+++") or line.startswith("---"):
                continue

            if line.startswith("+"):
                added_lines.append(line[1:])

            elif line.startswith("-"):
                removed_lines.append(line[1:])

        parsed_files.append({
            "file": file["path"],
            "status": file["status"],
            "additions": file["additions"],
            "deletions": file["deletions"],
            "changed_lines": changed_lines,
            "added_code": "\n".join(added_lines),
            "removed_code": "\n".join(removed_lines),
        })

    return parsed_files

def run_ruff(
    workspace: str,
    changed_files: list[str],
    changed_lines_by_file: dict[str, list[int]] | None = None,
) -> list[Finding]:
    """
    Run Ruff against the Python files in a repository workspace
    and convert Ruff findings into our common Finding model.
    """

    workspace_path = Path(workspace)

    python_files = [
    file
    for file in changed_files
    if file.endswith(".py")
]

    if not python_files:
        return []

    result = subprocess.run(
        [
            "ruff",
            "check",
            *python_files,
            "--output-format",
            "json",
        ],
        cwd=workspace,
        capture_output=True,
        text=True,
    )

    # Ruff returns exit code 1 when it finds violations.
    # That is not an execution failure for us.
    if result.returncode not in (0, 1):
        raise RuntimeError(
            f"Ruff failed: {result.stderr}"
        )

    if not result.stdout.strip():
        return []

    violations = json.loads(result.stdout)

    findings = []

    for violation in violations:
        relative_path = violation["filename"]

        fix = violation.get("fix") or {}

        changed_lines = (
            changed_lines_by_file or {}
        ).get(relative_path)

        if changed_lines is not None:
            violation_line = violation["location"]["row"]

            if violation_line not in changed_lines:
                continue

        severity, category = classify_finding(
            violation["code"],
            "ruff",
        )

        findings.append(
            Finding(
                severity=severity,
                category=category,
                file_path=relative_path,
                line_start=violation["location"]["row"],
                line_end=violation["end_location"]["row"],
                title=f"{violation['code']} {violation['message']}",
                description=(
                    f"Ruff detected {violation['code']}: "
                    f"{violation['message']}"
                ),
                suggestion=(
                    fix.get("message")
                    or "Review and correct this issue."
                ),
                confidence=0.95,
            )
        )
    return findings

def build_changed_lines_by_file(parsed_diffs: list[dict]) -> dict[str, list[int]]:
    """
    Build a mapping:

        file path -> changed line numbers
    """

    return {
        item["file"]: item["changed_lines"]
        for item in parsed_diffs
    }

def static_analyzer_agent(state: dict) -> dict:
    """
    Run language-specific static analyzers against
    the files changed by the PR.
    """

    changed_files = state["changed_files"]

    languages = detect_languages(changed_files)

    changed_lines_by_file = {
        file_path: diff["changed_lines"]
        for file_path, diff in state["diffs"].items()
    }

    workspace = state["repository_context"]["workspace"]

    findings = []

    # Python
    if "python" in languages:
        python_findings = run_ruff(
            workspace,
            changed_files,
            changed_lines_by_file,
        )

        findings.extend(python_findings)

    # JavaScript
    if "javascript" in languages:
        javascript_findings = run_eslint(
            workspace,
            changed_files,
            changed_lines_by_file,
        )

        findings.extend(javascript_findings)

    state["static_findings"] = findings

    return state