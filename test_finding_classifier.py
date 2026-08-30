"""
Unit tests for tools/finding_classifier.py

Run with:
    pytest test_finding_classifier.py -v
"""

from tools.finding_classifier import classify_finding


# ---------------------------------------------------------------------------
# Exact rule code matches — these are the specific examples from the
# project roadmap, so they must never regress.
# ---------------------------------------------------------------------------

def test_ruff_undefined_name_is_high_correctness():
    severity, category = classify_finding("F821", "ruff")
    assert severity == "HIGH"
    assert category == "correctness"


def test_ruff_unused_import_is_low_style():
    severity, category = classify_finding("F401", "ruff")
    assert severity == "LOW"
    assert category == "style"


def test_ruff_unused_variable_is_low_style():
    severity, category = classify_finding("F841", "ruff")
    assert severity == "LOW"
    assert category == "style"


def test_ruff_subprocess_without_check_is_medium_reliability():
    severity, category = classify_finding("PLW1510", "ruff")
    assert severity == "MEDIUM"
    assert category == "reliability"


def test_eslint_no_undef_is_high_correctness():
    severity, category = classify_finding("no-undef", "eslint")
    assert severity == "HIGH"
    assert category == "correctness"


# ---------------------------------------------------------------------------
# Security rules should be escalated
# ---------------------------------------------------------------------------

def test_ruff_sql_injection_is_critical_security():
    severity, category = classify_finding("S608", "ruff")
    assert severity == "CRITICAL"
    assert category == "security"


def test_eslint_eval_is_high_security():
    severity, category = classify_finding("no-eval", "eslint")
    assert severity == "HIGH"
    assert category == "security"


# ---------------------------------------------------------------------------
# Prefix-family fallback (Ruff) — codes NOT explicitly listed in the
# override table should still get a sensible classification based on
# their rule family.
# ---------------------------------------------------------------------------

def test_ruff_unmapped_bugbear_code_falls_back_to_reliability():
    # B024 isn't in our exact-match table, but starts with "B" (bugbear)
    severity, category = classify_finding("B024", "ruff")
    assert severity == "MEDIUM"
    assert category == "reliability"


def test_ruff_unmapped_pyflakes_code_falls_back_to_correctness():
    # F999 doesn't exist as a real rule, but should still hit the "F" family
    severity, category = classify_finding("F999", "ruff")
    assert severity == "MEDIUM"
    assert category == "correctness"


def test_ruff_pycodestyle_falls_back_to_style():
    severity, category = classify_finding("E501", "ruff")
    assert severity == "LOW"
    assert category == "style"


# ---------------------------------------------------------------------------
# Regression test: longer/more-specific prefixes must win over shorter
# ones. We hit this exact bug during development — "SIM108" was matching
# the generic "S" (security) family before "SIM" (simplify) was checked.
# ---------------------------------------------------------------------------

def test_simplify_prefix_does_not_get_misclassified_as_security():
    severity, category = classify_finding("SIM108", "ruff")
    assert severity == "LOW"
    assert category == "style"
    assert category != "security"  # explicit guard against the regression


# ---------------------------------------------------------------------------
# Unknown / unmapped rule codes should use the caller-supplied fallback,
# not silently crash or invent a category.
# ---------------------------------------------------------------------------

def test_unknown_eslint_rule_uses_fallback():
    severity, category = classify_finding(
        "some-custom-team-rule",
        "eslint",
        fallback_severity="LOW",
        fallback_category="style",
    )
    assert severity == "LOW"
    assert category == "style"


def test_no_rule_code_uses_fallback():
    severity, category = classify_finding(
        None,
        "ruff",
        fallback_severity="MEDIUM",
        fallback_category="style",
    )
    assert severity == "MEDIUM"
    assert category == "style"


def test_unknown_source_uses_fallback():
    severity, category = classify_finding(
        "F821",
        "some-other-tool",
        fallback_severity="LOW",
        fallback_category="style",
    )
    assert severity == "LOW"
    assert category == "style"