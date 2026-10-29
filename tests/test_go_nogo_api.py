
from fastapi.testclient import TestClient

from forgebid.api import app

client = TestClient(app)


def test_evaluate_bid_returns_needs_review_for_mandatory_gap():
    payload = {
        "evidence_report": {
            "rfp_title": "Sample Software RFP",
            "requirements": [
                {
                    "requirement_id": "REQ-SEC-001",
                    "mandatory": True,
                    "evidence_status": "CANDIDATE_EVIDENCE_FOUND",
                    "review_required": True,
                },
                {
                    "requirement_id": "REQ-DEL-002",
                    "mandatory": True,
                    "evidence_status": "NO_CLOSE_MATCH_FOUND",
                    "review_required": True,
                },
            ],
        }
    }

    response = client.post("/evaluate-bid", json=payload)

    assert response.status_code == 200

    result = response.json()
    assert result["recommendation"] == "NEEDS_REVIEW"
    assert result["mandatory_requirement_count"] == 2
    assert result["human_review_required"] is True
    assert result["issues"][0]["requirement_id"] == "REQ-DEL-002"


def test_evaluate_bid_accepts_candidate_evidence():
    payload = {
        "evidence_report": {
            "rfp_title": "Sample Software RFP",
            "requirements": [
                {
                    "requirement_id": "REQ-SEC-001",
                    "mandatory": True,
                    "evidence_status": "CANDIDATE_EVIDENCE_FOUND",
                    "review_required": True,
                }
            ],
        }
    }

    response = client.post("/evaluate-bid", json=payload)

    assert response.status_code == 200
    assert response.json()["recommendation"] == (
        "PRELIMINARY_GO_CANDIDATE"
    )
    assert response.json()["human_review_required"] is True


def test_evaluate_bid_rejects_missing_evidence_report():
    response = client.post("/evaluate-bid", json={})

    assert response.status_code == 422
