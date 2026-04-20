from pydantic import BaseModel, field_validator


# Inbound (request)

class ChecklistItem(BaseModel):
    name: str
    score: float = 0.0

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("item name must not be empty")
        return v


class ChecklistSection(BaseModel):
    title: str
    items: list[ChecklistItem]

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("section title must not be empty")
        return v

    @field_validator("items")
    @classmethod
    def items_not_empty(cls, v: list[ChecklistItem]) -> list[ChecklistItem]:
        if not v:
            raise ValueError("each section must have at least one item")
        return v


# Outbound (response)

class ItemResult(BaseModel):
    requirement: str
    score: float = 0.0
    status: str  # "pass" | "fail"
    reasoning: str
    evidence: str | None = None


class SectionResult(BaseModel):
    section: str
    items: list[ItemResult]


class AnalysisSummary(BaseModel):
    total: int
    passed: int
    failed: int
    total_score: float = 0.0
    passed_score: float = 0.0


class AnalysisResponse(BaseModel):
    summary: AnalysisSummary
    similarity_score: int
    results: list[SectionResult]
