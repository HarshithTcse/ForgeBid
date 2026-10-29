
from fastapi.testclient import TestClient

from forgebid import api


client = TestClient(api.app)


VALID_PAYLOAD = {
    "requirement": {
        "requirement_id": "REQ-SEC-001",
        "description": (
            "The supplier must demonstrate secure API development practices."
        ),
        "category": "security",
        "mandatory": True,
    },
    "top_k": 3,
}


class FakeCollection:
    def __init__(self, count):
        self._count = count

    def count(self):
        return self._count


class FakeKnowledgeBase:
    def __init__(self, count=1):
        self.collection = FakeCollection(count)


def test_retrieve_evidence_endpoint_success(monkeypatch):
    monkeypatch.setattr(
        api,
        "CompanyKnowledgeBase",
        FakeKnowledgeBase,
    )

    expected_result = {
        "requirement_id": "REQ-SEC-001",
        "requirement": VALID_PAYLOAD["requirement"]["description"],
        "category": "security",
        "mandatory": True,
        "evidence_found": True,
        "evidence": [
            {
                "text": "Apply input validation to API requests.",
                "source": "security_policy.md",
                "chunk_number": 0,
                "distance": 0.25,
            }
        ],
        "review_required": True,
        "note": "Retrieved evidence requires human verification.",
    }

    def fake_retrieve(requirement, knowledge_base, top_k=3):
        assert knowledge_base.collection.count() == 1
        assert requirement.requirement_id == "REQ-SEC-001"
        assert top_k == 3
        return expected_result

    monkeypatch.setattr(
        api,
        "retrieve_evidence_for_requirement",
        fake_retrieve,
    )

    response = client.post("/retrieve-evidence", json=VALID_PAYLOAD)

    assert response.status_code == 200
    assert response.json() == expected_result


def test_retrieve_evidence_rejects_empty_knowledge_base(monkeypatch):
    monkeypatch.setattr(
        api,
        "CompanyKnowledgeBase",
        lambda: FakeKnowledgeBase(count=0),
    )

    response = client.post("/retrieve-evidence", json=VALID_PAYLOAD)

    assert response.status_code == 409
    assert "Knowledge base is empty" in response.json()["detail"]


def test_retrieve_evidence_rejects_invalid_top_k():
    payload = {
        **VALID_PAYLOAD,
        "top_k": 0,
    }

    response = client.post("/retrieve-evidence", json=payload)

    assert response.status_code == 422
