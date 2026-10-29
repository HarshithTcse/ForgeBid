
from fastapi.testclient import TestClient

from forgebid import api


client = TestClient(api.app)


VALID_PAYLOAD = {
    "rfp": {
        "title": "Sample Software RFP",
        "submission_deadline": "2026-12-15",
        "requirements": [
            {
                "requirement_id": "REQ-SEC-001",
                "description": (
                    "The supplier must demonstrate secure API practices."
                ),
                "category": "security",
                "mandatory": True,
            }
        ],
        "evaluation_criteria": ["Technical capability"],
    },
    "top_k": 3,
    "max_distance": 0.45,
}


class FakeCollection:
    def __init__(self, count=1):
        self._count = count

    def count(self):
        return self._count


class FakeKnowledgeBase:
    def __init__(self, count=1):
        self.collection = FakeCollection(count)


def test_analyze_evidence_endpoint_success(monkeypatch):
    monkeypatch.setattr(
        api,
        "CompanyKnowledgeBase",
        FakeKnowledgeBase,
    )

    expected = {
        "rfp_title": "Sample Software RFP",
        "total_requirements": 1,
        "mandatory_requirements": 1,
        "optional_requirements": 0,
        "requirements": [],
        "review_required": True,
        "disclaimer": "Human verification is required.",
    }

    def fake_analyze(rfp, knowledge_base, top_k, max_distance):
        assert rfp.title == "Sample Software RFP"
        assert knowledge_base.collection.count() == 1
        assert top_k == 3
        assert max_distance == 0.45
        return expected

    monkeypatch.setattr(
        api,
        "analyze_rfp_evidence",
        fake_analyze,
    )

    response = client.post(
        "/analyze-evidence",
        json=VALID_PAYLOAD,
    )

    assert response.status_code == 200
    assert response.json() == expected


def test_analyze_evidence_rejects_empty_knowledge_base(monkeypatch):
    monkeypatch.setattr(
        api,
        "CompanyKnowledgeBase",
        lambda: FakeKnowledgeBase(count=0),
    )

    response = client.post(
        "/analyze-evidence",
        json=VALID_PAYLOAD,
    )

    assert response.status_code == 409
    assert "Knowledge base is empty" in response.json()["detail"]


def test_analyze_evidence_rejects_zero_top_k():
    payload = {**VALID_PAYLOAD, "top_k": 0}

    response = client.post(
        "/analyze-evidence",
        json=payload,
    )

    assert response.status_code == 422


def test_analyze_evidence_rejects_negative_distance():
    payload = {**VALID_PAYLOAD, "max_distance": -0.1}

    response = client.post(
        "/analyze-evidence",
        json=payload,
    )

    assert response.status_code == 422
