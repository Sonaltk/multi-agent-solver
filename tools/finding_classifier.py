# tools/finding_classifier.py

"""
Centralized severity/category classification for static analysis findings.

Ruff and ESLint each report a "rule code" (e.g. "F821", "no-undef").
This module maps rule codes to a consistent (severity, category) pair
so that findings from different tools/languages are comparable.

Severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
Category: "correctness" | "reliability" | "security" | "style"
"""

from typing import Literal

Severity = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
Category = Literal["correctness", "reliability", "security", "style"]

DEFAULT_SEVERITY: Severity = "LOW"
DEFAULT_CATEGORY: Category = "style"


# ---------------------------------------------------------------------------
# Ruff (Python) — exact rule code overrides
# ---------------------------------------------------------------------------
# These take priority over the prefix-family fallback below. Add specific
# codes here whenever the family default doesn't fit that particular rule.

RUFF_RULE_OVERRIDES: dict[str, tuple[Severity, Category]] = {
    # Pyflakes (F) — real correctness bugs
    "F821": ("HIGH", "correctness"),      # undefined name
    "F823": ("HIGH", "correctness"),      # used before assignment
    "F811": ("MEDIUM", "correctness"),    # redefinition of unused name
    "F632": ("MEDIUM", "correctness"),    # use of == with literal types
    "F702": ("HIGH", "correctness"),      # continue outside loop
    "F401": ("LOW", "style"),             # unused import
    "F841": ("LOW", "style"),             # unused variable

    # Pylint-ported (PL) — explicit examples from the roadmap
    "PLW1510": ("MEDIUM", "reliability"),  # subprocess.run without check=
    "PLW0603": ("LOW", "style"),           # global statement
    "PLE0704": ("HIGH", "correctness"),    # misplaced bare raise

    # Bugbear (B) — common real-world bug patterns
    "B006": ("HIGH", "reliability"),      # mutable default argument
    "B008": ("MEDIUM", "reliability"),    # function call in default arg
    "B012": ("MEDIUM", "reliability"),    # break/continue/return in finally

    # Bandit-derived security rules (S) — escalate the risky ones
    "S105": ("HIGH", "security"),         # hardcoded password
    "S106": ("HIGH", "security"),         # hardcoded password (call arg)
    "S107": ("HIGH", "security"),         # hardcoded password (default arg)
    "S301": ("HIGH", "security"),         # pickle usage
    "S324": ("MEDIUM", "security"),       # weak hash (md5/sha1)
    "S602": ("HIGH", "security"),         # subprocess with shell=True
    "S608": ("CRITICAL", "security"),     # possible SQL injection
    "S101": ("LOW", "style"),             # use of assert (often fine)

    # pycodestyle
    "E722": ("MEDIUM", "reliability"),    # bare except
    "E731": ("LOW", "style"),             # lambda assignment
}

# Ordered (longest-prefix-first) family fallback for Ruff codes that
# aren't in the exact-match table above. Covers the ~800+ codes we can't
# reasonably enumerate one by one.
RUFF_PREFIX_FAMILIES: list[tuple[str, Severity, Category]] = [
    ("PLE", "HIGH", "correctness"),     # pylint errors
    ("PLW", "MEDIUM", "reliability"),   # pylint warnings
    ("PLR", "LOW", "style"),            # pylint refactor suggestions
    ("PLC", "LOW", "style"),            # pylint conventions
    ("TRY", "MEDIUM", "reliability"),   # exception-handling anti-patterns
    ("BLE", "MEDIUM", "reliability"),   # blind except
    ("A0", "MEDIUM", "reliability"),    # shadowing a builtin
    ("SIM", "LOW", "style"),            # flake8-simplify (before bare "S")
    ("S", "HIGH", "security"),          # flake8-bandit security rules
    ("B", "MEDIUM", "reliability"),     # flake8-bugbear
    ("C90", "MEDIUM", "style"),         # mccabe complexity
    ("C4", "LOW", "style"),             # comprehension simplifications
    ("UP", "LOW", "style"),             # pyupgrade
    ("ANN", "LOW", "style"),            # missing type annotations
    ("ARG", "LOW", "style"),            # unused arguments
    ("RET", "LOW", "style"),            # return statement style
    ("N", "LOW", "style"),              # naming conventions
    ("I", "LOW", "style"),              # import sorting
    ("D", "LOW", "style"),              # docstring conventions
    ("T20", "LOW", "style"),            # print statement left in code
    ("E", "LOW", "style"),              # pycodestyle errors
    ("W", "LOW", "style"),              # pycodestyle warnings
    ("F", "MEDIUM", "correctness"),     # any other pyflakes code
]


# ---------------------------------------------------------------------------
# ESLint (JavaScript) — exact rule id overrides
# ---------------------------------------------------------------------------

ESLINT_RULE_OVERRIDES: dict[str, tuple[Severity, Category]] = {
    # Correctness
    "no-undef": ("HIGH", "correctness"),
    "no-const-assign": ("HIGH", "correctness"),
    "no-dupe-keys": ("HIGH", "correctness"),
    "no-dupe-args": ("HIGH", "correctness"),
    "no-unreachable": ("MEDIUM", "correctness"),
    "no-fallthrough": ("MEDIUM", "correctness"),
    "no-case-declarations": ("MEDIUM", "correctness"),
    "valid-typeof": ("HIGH", "correctness"),

    # Reliability
    "eqeqeq": ("MEDIUM", "reliability"),
    "no-debugger": ("MEDIUM", "reliability"),
    "no-empty": ("MEDIUM", "reliability"),
    "no-async-promise-executor": ("MEDIUM", "reliability"),
    "no-prototype-builtins": ("MEDIUM", "reliability"),
    "no-unsafe-optional-chaining": ("MEDIUM", "reliability"),

    # Security
    "no-eval": ("HIGH", "security"),
    "no-implied-eval": ("HIGH", "security"),
    "no-new-func": ("HIGH", "security"),
    "no-script-url": ("HIGH", "security"),

    # Style / maintainability
    "no-unused-vars": ("LOW", "style"),
    "no-console": ("LOW", "style"),
    "no-var": ("LOW", "style"),
    "prefer-const": ("LOW", "style"),
    "require-await": ("LOW", "style"),
    "complexity": ("MEDIUM", "style"),
}


# ---------------------------------------------------------------------------
# Bandit (Python security scanner) — exact rule code overrides
# ---------------------------------------------------------------------------
# Bandit assigns its own severity (LOW/MEDIUM/HIGH), but it tends to
# under-rate genuinely dangerous patterns (e.g. a hardcoded password is
# only "LOW" by Bandit's own scale). These overrides escalate the rules
# that matter most; anything not listed falls back to Bandit's own
# severity rating, translated 1:1 (Bandit doesn't have a CRITICAL tier).

BANDIT_RULE_OVERRIDES: dict[str, tuple[Severity, Category]] = {
    # Hardcoded secrets
    "B105": ("HIGH", "security"),   # hardcoded password (string)
    "B106": ("HIGH", "security"),   # hardcoded password (function arg)
    "B107": ("HIGH", "security"),   # hardcoded password (default arg)

    # Dangerous eval/exec
    "B102": ("HIGH", "security"),   # exec used
    "B307": ("HIGH", "security"),   # eval used

    # Unsafe deserialization
    "B301": ("HIGH", "security"),   # pickle.loads / pickle.load
    "B302": ("HIGH", "security"),   # marshal
    "B506": ("HIGH", "security"),   # yaml.load without SafeLoader

    # Command / SQL injection
    "B602": ("HIGH", "security"),       # subprocess with shell=True
    "B603": ("MEDIUM", "security"),     # subprocess without shell (partial path risk)
    "B605": ("HIGH", "security"),       # os.system
    "B609": ("HIGH", "security"),       # wildcard injection
    "B608": ("CRITICAL", "security"),   # SQL injection via string building

    # Weak crypto
    "B324": ("MEDIUM", "security"),     # weak hash (md5/sha1)

    # Framework misconfiguration
    "B201": ("HIGH", "security"),       # Flask app.run(debug=True)
    "B701": ("HIGH", "security"),       # Jinja2 autoescape disabled

    # Low-value "you imported a risky module" noise — downgrade so these
    # don't drown out findings about how the module is actually *used*.
    "B403": ("LOW", "style"),   # import pickle
    "B404": ("LOW", "style"),   # import subprocess
    "B405": ("LOW", "style"),   # import xml.etree
    "B410": ("LOW", "style"),   # import lxml
    "B411": ("LOW", "style"),   # import xmlrpclib

    "B108": ("LOW", "style"),          # hardcoded /tmp path
    "B104": ("MEDIUM", "reliability"), # binding to 0.0.0.0
}


def classify_finding(
    rule_code: str | None,
    source: Literal["ruff", "eslint", "bandit"],
    fallback_severity: Severity = DEFAULT_SEVERITY,
    fallback_category: Category = DEFAULT_CATEGORY,
) -> tuple[Severity, Category]:
    """
    Return (severity, category) for a given rule code from a given tool.

    Lookup order:
      1. Exact rule code match for that tool.
      2. (Ruff only) longest matching prefix family.
      3. The caller-supplied fallback (e.g. ESLint's own error/warn level),
         or the module default if the caller doesn't have a better guess.
    """

    if not rule_code:
        return fallback_severity, fallback_category

    if source == "ruff":
        if rule_code in RUFF_RULE_OVERRIDES:
            return RUFF_RULE_OVERRIDES[rule_code]

        # Sort by prefix length (longest first) so a specific family like
        # "SIM" is checked before a shorter, more general one like "S",
        # regardless of how RUFF_PREFIX_FAMILIES happens to be ordered.
        for prefix, severity, category in sorted(
            RUFF_PREFIX_FAMILIES, key=lambda f: len(f[0]), reverse=True
        ):
            if rule_code.startswith(prefix):
                return severity, category

        return fallback_severity, fallback_category

    if source == "eslint":
        if rule_code in ESLINT_RULE_OVERRIDES:
            return ESLINT_RULE_OVERRIDES[rule_code]

        return fallback_severity, fallback_category

    if source == "bandit":
        if rule_code in BANDIT_RULE_OVERRIDES:
            return BANDIT_RULE_OVERRIDES[rule_code]

        # Fall back to whatever Bandit's own severity rating was
        # (passed in by the caller), category is always security
        # unless explicitly downgraded above.
        return fallback_severity, fallback_category

    return fallback_severity, fallback_category