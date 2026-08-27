from typing import Any, Literal, TypedDict


from pydantic import BaseModel, Field
from typing import Any

class Finding(BaseModel):
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    category: str
    file_path: str

    line_start: int
    line_end: int

    title: str
    description: str
    suggestion: str

    confidence: float = Field(ge=0.0, le=1.0)

class ReviewState(TypedDict):
    review_id: str

    repository: str
    pr_number: int

    base_sha: str
    head_sha: str

    pr_title: str
    pr_description: str

    changed_files: list[str]
    diffs: dict[str, str]

    repository_context: dict[str, Any]

    static_findings: list[Finding]
    security_findings: list[Finding]
    style_findings: list[Finding]
    architecture_findings: list[Finding]

    merged_findings: list[Finding]

    review_summary: str

    status: str