from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    row_id: str
    source_platform: str
    original_taxonomy: str
    parsed_components: dict[str, str]
    validation_status: str
    error_types: list[str]
    suggested_corrected_taxonomy: str | None = None
    confidence_score: float = 0.0
    review_status: str
    sync_status: str


class ReviewDecision(BaseModel):
    reviewer_id: int
    action: str = Field(pattern="^(accept|reject|amend)$")
    final_taxonomy: str
    comments: str | None = None


class SyncRequest(BaseModel):
    platform: str = "meta"
    dry_run: bool = True
    record_ids: list[int]
