
from forgebid.models import RFPDocument, Requirement
from forgebid.bid_readiness import assess_bid_readiness


def test_missing_information_requires_review():
    rfp = RFPDocument(title="Sample RFP")

    result = assess_bid_readiness(rfp)

    assert result.readiness_status == "NEEDS_REVIEW"
    assert result.mandatory_requirement_count == 0
    assert result.optional_requirement_count == 0
    assert len(result.issues) >= 3


def test_requirement_counts_are_correct():
    rfp = RFPDocument(
        title="Website Development RFP",
        submission_deadline="2026-12-01",
        requirements=[
            Requirement(
                requirement_id="REQ-001",
                description="Use HTTPS encryption",
                category="security",
                mandatory=True,
            ),
            Requirement(
                requirement_id="REQ-002",
                description="Provide optional training",
                category="support",
                mandatory=False,
            ),
        ],
        evaluation_criteria=["Technical quality", "Cost"],
    )

    result = assess_bid_readiness(rfp)

    assert result.mandatory_requirement_count == 1
    assert result.optional_requirement_count == 1


def test_missing_deadline_is_flagged():
    rfp = RFPDocument(
        title="Website RFP",
        requirements=[
            Requirement(
                requirement_id="REQ-001",
                description="Use HTTPS",
                category="security",
                mandatory=True,
            )
        ],
        evaluation_criteria=["Technical quality"],
    )

    result = assess_bid_readiness(rfp)

    assert result.readiness_status == "NEEDS_REVIEW"
    assert any(
        "deadline" in issue.issue.lower()
        for issue in result.issues
    )


def test_complete_extracted_data_allows_human_review():
    rfp = RFPDocument(
        title="Website Development RFP",
        submission_deadline="2026-12-01",
        requirements=[
            Requirement(
                requirement_id="REQ-001",
                description="Use HTTPS encryption",
                category="security",
                mandatory=True,
            )
        ],
        evaluation_criteria=["Technical quality", "Cost"],
    )

    result = assess_bid_readiness(rfp)

    assert result.readiness_status == "READY_FOR_HUMAN_REVIEW"
    assert result.mandatory_requirement_count == 1
    assert result.optional_requirement_count == 0
    assert result.issues == []
