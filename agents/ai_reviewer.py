# agents/ai_reviewer.py

import json

from langchain_groq import ChatGroq

from models.review import Finding

# The LLM client is created lazily (inside get_llm(), not here at import
# time) so this module can be imported and its pure functions tested
# without a GROQ_API_KEY being set — only ai_reviewer_agent() actually
# needs one, since that's the only function that makes a real call.
_llm = None


def get_llm():
    global _llm
    if _llm is None:
        # temperature=0 because this is an analytical/structured-output
        # task — we want consistent, parseable JSON, not creative variance.
        _llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    return _llm


def format_findings(findings: list[Finding]) -> str:
    """
    Render a list of Finding objects as a readable block of text
    for inclusion in the LLM prompt.
    """

    if not findings:
        return "(none)"

    lines = []
    for f in findings:
        lines.append(
            f"- [{f.severity}/{f.category}] {f.file_path}:{f.line_start} "
            f"{f.title} — {f.description}"
        )
    return "\n".join(lines)


def format_diffs(diffs: dict[str, str]) -> str:
    """
    Render the PR's per-file diffs as a readable block of text.
    Truncates very large diffs so we don't blow the context window.
    """

    if not diffs:
        return "(no diff available)"

    MAX_CHARS_PER_FILE = 4000

    blocks = []
    for file_path, patch in diffs.items():
        truncated = patch[:MAX_CHARS_PER_FILE]
        if len(patch) > MAX_CHARS_PER_FILE:
            truncated += "\n... (truncated)"
        blocks.append(f"--- {file_path} ---\n{truncated}")

    return "\n\n".join(blocks)


def build_review_prompt(state: dict) -> str:
    static_findings = state.get("static_findings", [])
    security_findings = state.get("security_findings", [])

    return f"""
You are a senior software engineer performing a pull request code review.

PR Title:
{state.get("pr_title", "(no title)")}

PR Description:
{state.get("pr_description", "(no description)")}

Diff:
{format_diffs(state.get("diffs", {}))}

Static analysis findings (from Ruff/ESLint):
{format_findings(static_findings)}

Security findings (from Bandit):
{format_findings(security_findings)}

Your job:
1. Understand what this PR is trying to do.
2. Identify any logical bugs or missing edge cases in the diff that the
   static/security tools above would not catch.
3. Look at the findings listed above and flag any that look like false
   positives given the actual context of the code (be conservative —
   only flag ones you're genuinely confident about).
4. Decide an overall verdict: "approve" if there are no HIGH/CRITICAL
   issues remaining, otherwise "request_changes".
5. Write a short (3-5 sentence) plain-English review summary.

Respond with ONLY valid JSON in exactly this shape, no markdown fences,
no extra commentary before or after:

{{
  "additional_findings": [
    {{
      "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
      "category": "correctness" | "reliability" | "security" | "style",
      "file_path": "string",
      "line_start": 0,
      "line_end": 0,
      "title": "string",
      "description": "string",
      "suggestion": "string",
      "confidence": 0.0
    }}
  ],
  "likely_false_positives": [
    {{"title": "string (must match a finding title above)", "reason": "string"}}
  ],
  "verdict": "approve" | "request_changes",
  "summary": "string"
}}

If there are no additional findings or false positives, use empty arrays.
"""


def parse_ai_response(raw_text: str) -> dict:
    """
    Parse the LLM's JSON response, tolerating common formatting quirks
    like markdown code fences around the JSON block.
    """

    cleaned = raw_text.strip()

    if cleaned.startswith("```"):
        # Strip a leading ```json or ``` and a trailing ```
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[len("json"):]
        cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"AI reviewer returned invalid JSON: {e}\nRaw response:\n{raw_text}"
        )


def ai_reviewer_agent(state: dict) -> dict:
    """
    Run the AI review layer: understand PR intent, surface additional
    logical findings, flag likely false positives among existing
    findings, and produce a verdict + summary.
    """

    prompt = build_review_prompt(state)

    response = get_llm().invoke(prompt)

    parsed = parse_ai_response(response.content)

    additional_findings = [
        Finding(**f) for f in parsed.get("additional_findings", [])
    ]

    state["ai_findings"] = additional_findings
    state["likely_false_positives"] = parsed.get("likely_false_positives", [])
    state["ai_verdict"] = parsed.get("verdict", "request_changes")
    state["review_summary"] = parsed.get("summary", "")

    return state