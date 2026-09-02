# agents/finding_merger.py

from models.review import Finding

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}


def is_flagged_false_positive(
    finding: Finding,
    flagged: list[dict[str, str]],
) -> bool:
    """
    Check whether the AI reviewer flagged this finding as a likely
    false positive. Matches on title, case-insensitive, allowing
    either an exact match or the flagged title being a substring
    (since the AI may not reproduce the exact original title verbatim).
    """

    finding_title = finding.title.lower()

    for entry in flagged:
        flagged_title = entry.get("title", "").lower().strip()
        if not flagged_title:
            continue
        if flagged_title == finding_title or flagged_title in finding_title:
            return True

    return False


def dedupe_findings(findings: list[Finding]) -> list[Finding]:
    """
    Collapse findings that point at the same file + line into a single
    finding, keeping the highest-severity version. This mainly catches
    cases where the AI reviewer independently flags something a static
    tool already caught on the same line.
    """

    best_by_location: dict[tuple[str, int], Finding] = {}

    for finding in findings:
        key = (finding.file_path, finding.line_start)

        existing = best_by_location.get(key)

        if existing is None:
            best_by_location[key] = finding
            continue

        existing_rank = SEVERITY_ORDER.get(existing.severity, 99)
        new_rank = SEVERITY_ORDER.get(finding.severity, 99)

        if new_rank < existing_rank:
            best_by_location[key] = finding
        # if equal or lower severity, keep the one already there
        # (first-seen wins the tie, which favors static/security
        # tool findings since they're added before ai_findings)

    return list(best_by_location.values())


def sort_findings(findings: list[Finding]) -> list[Finding]:
    return sorted(
        findings,
        key=lambda f: (
            SEVERITY_ORDER.get(f.severity, 99),
            f.file_path,
            f.line_start,
        ),
    )


def format_review(
    merged_findings: list[Finding],
    verdict: str,
    summary: str,
) -> str:
    """
    Produce a human-readable review report, grouped by severity.
    This mirrors the format sketched in the project roadmap
    (Phase 8 — GitHub review output) but just as printable text for now;
    actually posting it to GitHub is a separate later step.
    """

    verdict_line = (
        "✅ Approved"
        if verdict == "approve"
        else "❌ Changes requested"
    )

    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for f in merged_findings:
        if f.severity in counts:
            counts[f.severity] += 1

    lines = [
        verdict_line,
        "",
        summary,
        "",
        (
            f"Findings: {counts['CRITICAL']} critical, "
            f"{counts['HIGH']} high, "
            f"{counts['MEDIUM']} medium, "
            f"{counts['LOW']} low"
        ),
        "",
    ]

    for f in merged_findings:
        lines.append(f"{f.severity} — {f.category}")
        lines.append(f"{f.file_path}:{f.line_start}")
        lines.append("")
        lines.append(f.description)
        lines.append("")
        lines.append(f"Suggested fix: {f.suggestion}")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def finding_merger_agent(state: dict) -> dict:
    """
    Combine static, security, and AI findings into one deduplicated,
    severity-sorted list, dropping anything the AI reviewer flagged
    as a likely false positive. Also builds a formatted review report.
    """

    all_findings = (
        state.get("static_findings", [])
        + state.get("security_findings", [])
        + state.get("ai_findings", [])
    )

    flagged = state.get("likely_false_positives", [])

    kept = [
        f for f in all_findings
        if not is_flagged_false_positive(f, flagged)
    ]

    deduped = dedupe_findings(kept)
    merged = sort_findings(deduped)

    state["merged_findings"] = merged

    state["formatted_review"] = format_review(
        merged,
        state.get("ai_verdict", "request_changes"),
        state.get("review_summary", ""),
    )

    return state