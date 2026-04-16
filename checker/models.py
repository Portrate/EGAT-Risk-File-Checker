from pydantic import BaseModel, field_validator


# ── Inbound (request) ──────────────────────────────────────────────────────────

class ChecklistSection(BaseModel):
    title: str
    items: list[str]

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("section title must not be empty")
        return v

    @field_validator("items")
    @classmethod
    def items_not_empty(cls, v: list[str]) -> list[str]:
        cleaned = [i.strip() for i in v if i.strip()]
        if not cleaned:
            raise ValueError("each section must have at least one item")
        return cleaned


# ── Outbound (response) ────────────────────────────────────────────────────────

class ItemResult(BaseModel):
    requirement: str
    status: str  # "pass" | "fail" | "partial"
    reasoning: str
    evidence: str | None = None


class SectionResult(BaseModel):
    section: str
    items: list[ItemResult]


class AnalysisSummary(BaseModel):
    total: int
    passed: int
    failed: int


class AnalysisResponse(BaseModel):
    summary: AnalysisSummary
    similarity_score: int
    results: list[SectionResult]
