"""
Unit tests for agents/finding_merger.py

Run with:
    pytest test_finding_merger.py -v
"""

from agents.finding_merger import (
    is_flagged_false_positive,
    dedupe_findings,
    sort_findings,
    format_review,
    finding_merger_agent,
)
from models.review import Finding


def make_finding(
    severity="MEDIUM",
    category="style",
    file_path="app.py",
    line_start=10,
    title="Some issue",
    description="Something is wrong",
    suggestion="Fix it",
    confidence=0.7,
):
    return Finding(
        severity=severity,
        category=category,
        file_path=file_path,
        line_start=line_start,
        line_end=line_start,
        title=title,
        description=description,
        suggestion=suggestion,
        confidence=confidence,
    )


# ---------------------------------------------------------------------------
# False positive filtering
# ---------------------------------------------------------------------------

def test_flagged_false_positive_is_detected_exact_match():
    finding = make_finding(title="F401 unused import")
    flagged = [{"title": "F401 unused import", "reason": "used in __all__"}]
    assert is_flagged_false_positive(finding, flagged) is True


def test_flagged_false_positive_is_case_insensitive():
    finding = make_finding(title="F401 Unused Import")
    flagged = [{"title": "f401 unused import", "reason": "used in __all__"}]
    assert is_flagged_false_positive(finding, flagged) is True


def test_unflagged_finding_is_not_a_false_positive():
    finding = make_finding(title="F821 undefined name")
    flagged = [{"title": "F401 unused import", "reason": "used in __all__"}]
    assert is_flagged_false_positive(finding, flagged) is False


def test_no_flagged_list_means_nothing_is_a_false_positive():
    finding = make_finding(title="F821 undefined name")
    assert is_flagged_false_positive(finding, []) is False


# ---------------------------------------------------------------------------
# Dedup
# ---------------------------------------------------------------------------

def test_dedupe_keeps_single_finding_for_unique_locations():
    findings = [
        make_finding(file_path="a.py", line_start=1),
        make_finding(file_path="b.py", line_start=1),
    ]
    result = dedupe_findings(findings)
    assert len(result) == 2


def test_dedupe_collapses_same_file_and_line():
    findings = [
        make_finding(file_path="a.py", line_start=5, severity="LOW", title="tool finding"),
        make_finding(file_path="a.py", line_start=5, severity="HIGH", title="ai finding"),
    ]
    result = dedupe_findings(findings)
    assert len(result) == 1
    assert result[0].severity == "HIGH"
    assert result[0].title == "ai finding"


def test_dedupe_tie_keeps_first_seen():
    findings = [
        make_finding(file_path="a.py", line_start=5, severity="MEDIUM", title="first"),
        make_finding(file_path="a.py", line_start=5, severity="MEDIUM", title="second"),
    ]
    result = dedupe_findings(findings)
    assert len(result) == 1
    assert result[0].title == "first"


# ---------------------------------------------------------------------------
# Sort
# ---------------------------------------------------------------------------

def test_sort_orders_by_severity_critical_first():
    findings = [
        make_finding(severity="LOW", file_path="a.py", line_start=1),
        make_finding(severity="CRITICAL", file_path="a.py", line_start=2),
        make_finding(severity="MEDIUM", file_path="a.py", line_start=3),
        make_finding(severity="HIGH", file_path="a.py", line_start=4),
    ]
    result = sort_findings(findings)
    assert [f.severity for f in result] == ["CRITICAL", "HIGH", "MEDIUM", "LOW"]


def test_sort_is_stable_within_same_severity_by_file_then_line():
    findings = [
        make_finding(severity="HIGH", file_path="b.py", line_start=1),
        make_finding(severity="HIGH", file_path="a.py", line_start=5),
        make_finding(severity="HIGH", file_path="a.py", line_start=2),
    ]
    result = sort_findings(findings)
    assert [(f.file_path, f.line_start) for f in result] == [
        ("a.py", 2), ("a.py", 5), ("b.py", 1)
    ]


# ---------------------------------------------------------------------------
# Formatted review text
# ---------------------------------------------------------------------------

def test_format_review_shows_approved_verdict():
    output = format_review([], "approve", "Looks good.")
    assert "Approved" in output
    assert "Looks good." in output


def test_format_review_shows_changes_requested_verdict():
    finding = make_finding(severity="HIGH", title="bug")
    output = format_review([finding], "request_changes", "Found an issue.")
    assert "Changes requested" in output
    assert "bug" not in output  # title isn't rendered, but description is
    assert "1 high" in output


# ---------------------------------------------------------------------------
# Full agent behavior
# ---------------------------------------------------------------------------

def test_finding_merger_agent_combines_all_sources_and_drops_false_positives():
    state = {
        "static_findings": [
            make_finding(file_path="a.py", line_start=1, severity="LOW", title="F401 unused import"),
        ],
        "security_findings": [
            make_finding(file_path="b.py", line_start=2, severity="CRITICAL", title="B608 sql injection"),
        ],
        "ai_findings": [
            make_finding(file_path="c.py", line_start=3, severity="HIGH", title="off-by-one bug"),
        ],
        "likely_false_positives": [
            {"title": "F401 unused import", "reason": "used in __all__"},
        ],
        "ai_verdict": "request_changes",
        "review_summary": "Found a critical SQL injection issue.",
    }

    result = finding_merger_agent(state)

    # false positive dropped, so only 2 of the original 3 remain
    assert len(result["merged_findings"]) == 2
    assert result["merged_findings"][0].severity == "CRITICAL"
    assert "formatted_review" in result
    assert "Changes requested" in result["formatted_review"]