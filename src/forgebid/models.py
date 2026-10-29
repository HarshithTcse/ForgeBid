
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


class BidReadinessIssue(BaseModel):
    issue: str
    severity: str
    reason: str


class BidReadinessAssessment(BaseModel):
    rfp_title: str
    readiness_status: str
    mandatory_requirement_count: int
    optional_requirement_count: int
    issues: list[BidReadinessIssue] = Field(default_factory=list)
    checks_required: list[str] = Field(default_factory=list)
    recommendation: str

class RFPAnalysisReport(BaseModel):
    extracted_rfp: RFPDocument
    readiness_assessment: BidReadinessAssessment
