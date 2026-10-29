
from forgebid.go_nogo import evaluate_bid_readiness


def test_missing_mandatory_evidence_requires_review():
    report = {
        "rfp_title": "Sample RFP",
        "requirements": [
            {
                "requirement_id": "REQ-1",
                "mandatory": True,
                "evidence_status": "NO_CLOSE_MATCH_FOUND",
                "review_required": True,
            }
        ],
    }

    result = evaluate_bid_readiness(report)

    assert result["recommendation"] == "NEEDS_REVIEW"
    assert result["human_review_required"] is True
    assert result["issues"][0]["type"] == "MANDATORY_EVIDENCE_GAP"


def test_candidate_evidence_allows_preliminary_go_candidate():
    report = {
        "rfp_title": "Sample RFP",
        "requirements": [
            {
                "requirement_id": "REQ-1",
                "mandatory": True,
                "evidence_status": "CANDIDATE_EVIDENCE_FOUND",
                "review_required": True,
            },
            {
                "requirement_id": "REQ-2",
                "mandatory": False,
                "evidence_status": "NO_CLOSE_MATCH_FOUND",
                "review_required": True,
            },
        ],
    }

    result = evaluate_bid_readiness(report)

    assert result["recommendation"] == "PRELIMINARY_GO_CANDIDATE"
    assert result["mandatory_requirement_count"] == 1
    assert result["requirements_reviewed"] == 2
    assert result["human_review_required"] is True


def test_empty_requirements_require_review():
    result = evaluate_bid_readiness({
        "rfp_title": "Empty RFP",
        "requirements": [],
    })

    assert result["recommendation"] == "NEEDS_REVIEW"
    assert result["requirements_reviewed"] == 0


def test_no_mandatory_requirements_does_not_claim_final_go():
    report = {
        "rfp_title": "Optional Requirements RFP",
        "requirements": [
            {
                "requirement_id": "REQ-1",
                "mandatory": False,
                "evidence_status": "CANDIDATE_EVIDENCE_FOUND",
                "review_required": True,
            }
        ],
    }

    result = evaluate_bid_readiness(report)

    assert result["recommendation"] == "PRELIMINARY_GO_CANDIDATE"
    assert result["human_review_required"] is True
    assert result["limitations"]
