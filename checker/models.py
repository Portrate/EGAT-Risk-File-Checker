from pydantic import BaseModel, field_validator


# Inbound (request) — models describing the checklist submitted by the user

# Represents a single sub-item (รายการย่อย) inside a checklist section
class ChecklistItem(BaseModel):
    name: str           # text of the requirement (e.g. "สรุปผลการบริหารความเสี่ยง")
    score: float = 0.0  # weight of this item; 0.0 means unweighted

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        # Strip whitespace then reject blank names
        v = v.strip()
        if not v:
            raise ValueError("item name must not be empty")
        return v

# Represents a top-level section (หัวข้อหลัก) that groups one or more ChecklistItems
class ChecklistSection(BaseModel):
    title: str                 # section heading (e.g. "บทสรุปผู้บริหาร")
    items: list[ChecklistItem] # must contain at least one item

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        # Strip whitespace then reject blank titles
        v = v.strip()
        if not v:
            raise ValueError("section title must not be empty")
        return v

    @field_validator("items")
    @classmethod
    def items_not_empty(cls, v: list[ChecklistItem]) -> list[ChecklistItem]:
        # Require at least one item so the LLM always has something to evaluate
        if not v:
            raise ValueError("each section must have at least one item")
        return v


# Outbound (response) — models representing the LLM analysis result

# LLM verdict for a single checklist sub-item
class ItemResult(BaseModel):
    requirement: str        # mirrors ChecklistItem.name for traceability
    score: float = 0.0      # score awarded (0 up to the item's weight)
    status: str             # "pass" | "fail"
    reasoning: str          # Thai-language explanation from the LLM
    evidence: str | None = None  # verbatim excerpt from the document, or None if not found

# Aggregated LLM results for one top-level section
class SectionResult(BaseModel):
    section: str            # mirrors ChecklistSection.title
    items: list[ItemResult] # one ItemResult per ChecklistItem in the section

# High-level counts and scores summarising the entire analysis
class AnalysisSummary(BaseModel):
    total: int              # total number of sub-items checked
    passed: int             # number of items with status "pass"
    failed: int             # number of items with status "fail"
    total_score: float = 0.0   # sum of all possible item scores
    passed_score: float = 0.0  # sum of scores for passed items only

# Top-level response returned by POST /analyze
class AnalysisResponse(BaseModel):
    summary: AnalysisSummary
    similarity_score: int   # 0-100 overall similarity between document and checklist
    results: list[SectionResult]
