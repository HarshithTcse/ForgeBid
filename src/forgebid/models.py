
from pydantic import BaseModel, Field


class Requirement(BaseModel):
    requirement_id: str
    description: str
    category: str
    mandatory: bool = False


class RFPDocument(BaseModel):
    title: str
    submission_deadline: str | None = None
    requirements: list[Requirement] = Field(default_factory=list)
    evaluation_criteria: list[str] = Field(default_factory=list)
