
from forgebid.models import (
    BidReadinessAssessment,
    BidReadinessIssue,
    RFPDocument,
)


def assess_bid_readiness(
    rfp: RFPDocument,
) -> BidReadinessAssessment:
    """Assess RFP readiness using transparent, deterministic rules."""

    issues: list[BidReadinessIssue] = []
    checks_required: list[str] = []

    mandatory_count = sum(
        1 for requirement in rfp.requirements
        if requirement.mandatory
    )
    optional_count = len(rfp.requirements) - mandatory_count

    if not rfp.title.strip() or rfp.title.startswith("["):
        issues.append(
            BidReadinessIssue(
                issue="RFP title needs verification",
                severity="medium",
                reason="The title is empty or may still be a template placeholder.",
            )
        )

    if not rfp.submission_deadline:
        issues.append(
            BidReadinessIssue(
                issue="Submission deadline is unknown",
                severity="high",
                reason="Confirm the deadline in the original RFP before planning submission.",
            )
        )
        checks_required.append(
            "Verify the official submission deadline and time zone."
        )

    if not rfp.requirements:
        issues.append(
            BidReadinessIssue(
                issue="No requirements extracted",
                severity="high",
                reason="The RFP may need reprocessing or manual review.",
            )
        )
        checks_required.append(
            "Review the original RFP and verify requirement extraction."
        )

    if not rfp.evaluation_criteria:
        issues.append(
            BidReadinessIssue(
                issue="Evaluation criteria are unavailable",
                severity="medium",
                reason="The scoring method could not be confirmed from the extracted data.",
            )
        )
        checks_required.append(
            "Find and verify the evaluation and scoring criteria in the original RFP."
        )

    if mandatory_count:
        checks_required.append(
            "Confirm that the company can satisfy every mandatory requirement."
        )

    checks_required.append(
        "Verify supporting evidence, resources, costs, and delivery capability."
    )

    if issues:
        status = "NEEDS_REVIEW"
        recommendation = (
            "Do not make a final Go/No-Go decision yet. Resolve the listed "
            "issues and verify the RFP against the original document."
        )
    else:
        status = "READY_FOR_HUMAN_REVIEW"
        recommendation = (
            "The initial automated checks found no missing key fields. "
            "A human reviewer must still confirm compliance and bid suitability."
        )

    return BidReadinessAssessment(
        rfp_title=rfp.title,
        readiness_status=status,
        mandatory_requirement_count=mandatory_count,
        optional_requirement_count=optional_count,
        issues=issues,
        checks_required=checks_required,
        recommendation=recommendation,
    )
