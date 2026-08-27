import json
import subprocess
from pathlib import Path

from models.review import Finding


def has_eslint_config(workspace: Path) -> bool:
    """
    Check whether the repository provides an ESLint configuration
    that ESLint 9+ can use.
    """

    config_files = [
        "eslint.config.js",
        "eslint.config.mjs",
        "eslint.config.cjs",
    ]

    return any(
        (workspace / config).exists()
        for config in config_files
    )


def run_eslint(
    workspace: str,
    changed_files: list[str],
    changed_lines_by_file: dict[str, list[int]],
) -> list[Finding]:
    """
    Run ESLint against JavaScript files changed by a PR.

    If the repository does not provide a compatible ESLint
    configuration, skip ESLint gracefully.
    """

    workspace_path = Path(workspace)

    js_files = [
        file
        for file in changed_files
        if Path(file).suffix.lower() in {
            ".js",
            ".jsx",
            ".mjs",
            ".cjs",
        }
    ]

    if not js_files:
        return []

    # Don't try to run ESLint if the repository has no
    # ESLint 9+ configuration.
    if not has_eslint_config(workspace_path):
        print("ESLint skipped: no compatible ESLint configuration found.")
        return []

    findings = []

    for file_path in js_files:
        absolute_path = workspace_path / file_path

        if not absolute_path.exists():
            continue

        print(f"Running ESLint on: {file_path}")

        try:
            result = subprocess.run(
                [
                    "npx",
                    "--no-install",
                    "eslint",
                    str(absolute_path),
                    "--format",
                    "json",
                ],
                cwd=workspace_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

        except subprocess.TimeoutExpired:
            print(
                f"ESLint skipped for {file_path}: "
                "analysis timed out."
            )
            continue

        print(f"ESLint finished: {file_path}")

        if result.returncode not in (0, 1):
            print(
                f"ESLint skipped for {file_path}: "
                f"{result.stderr.strip()}"
            )
            continue

        if not result.stdout.strip():
            continue

        try:
            results = json.loads(result.stdout)
        except json.JSONDecodeError:
            print(
                f"ESLint skipped for {file_path}: "
                "invalid JSON output."
            )
            continue

        changed_lines = set(
            changed_lines_by_file.get(file_path, [])
        )

        for result_file in results:
            for violation in result_file.get("messages", []):
                line = violation.get("line")

                # Only report issues on lines changed by the PR.
                if line not in changed_lines:
                    continue

                severity = (
                    "HIGH"
                    if violation["severity"] == 2
                    else "LOW"
                )

                suggestion = "Review and correct this issue."

                suggestions = violation.get("suggestions", [])

                if suggestions:
                    suggestion = suggestions[0].get(
                        "desc",
                        suggestion,
                    )

                findings.append(
                    Finding(
                        severity=severity,
                        category="style",
                        file_path=file_path,
                        line_start=line,
                        line_end=violation.get(
                            "endLine",
                            line,
                        ),
                        title=violation.get(
                            "ruleId",
                            "ESLint violation",
                        ),
                        description=violation["message"],
                        suggestion=suggestion,
                        confidence=0.95,
                    )
                )

    return findings