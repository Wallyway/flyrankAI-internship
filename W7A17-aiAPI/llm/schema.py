from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Category(str, Enum):
    BUG = "bug"
    FEATURE = "feature"
    CHORE = "chore"
    DOCS = "docs"
    OTHER = "other"


class Urgency(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class Source(str, Enum):
    MODEL = "model"
    STUB = "stub"
    FALLBACK = "fallback"


class TriageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=2000)


class TriageResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: Category
    urgency: Urgency
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str = Field(min_length=1, max_length=300)


class TriageResponse(TriageResult):
    source: Source


STUB_RESULT = TriageResult(
    category=Category.BUG,
    urgency=Urgency.NORMAL,
    confidence=0.9,
    reason="Stub mode is on, so no model was called.",
)

FALLBACK_RESULT = TriageResult(
    category=Category.OTHER,
    urgency=Urgency.NORMAL,
    confidence=0.0,
    reason="AI triage is disabled, so this task was not classified.",
)
