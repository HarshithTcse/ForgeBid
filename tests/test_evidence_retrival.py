
import pytest

from forgebid.evidence_retrieval import retrieve_evidence_for_requirement
from forgebid.models import Requirement


class FakeKnowledgeBase:
    """Simulate retrieval without loading models or calling external APIs."""

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        assert query == "The supplier must demonstrate secure API practices."
        assert top_k == 3

        return [
            {
                "text": "Apply input validation to API requests.",
                "source": "security_policy.md",
                "chunk_number": 0,
                "distance": 0.25,
            }
        ]


def make_requirement(description: str) -> Requirement:
    return Requirement(
        requirement_id="REQ-SEC-001",
        description=description,
        category="security",
        mandatory=True,
    )


def test_retrieves_evidence_for_requirement():
    requirement = make_requirement(
        "The supplier must demonstrate secure API practices."
    )

    result = retrieve_evidence_for_requirement(
        requirement,
        FakeKnowledgeBase(),
    )

    assert result["requirement_id"] == "REQ-SEC-001"
    assert result["evidence_found"] is True
    assert result["evidence"][0]["source"] == "security_policy.md"
    assert result["evidence"][0]["text"] == (
        "Apply input validation to API requests."
    )


def test_marks_human_review_as_required():
    requirement = make_requirement(
        "The supplier must demonstrate secure API practices."
    )

    result = retrieve_evidence_for_requirement(
        requirement,
        FakeKnowledgeBase(),
    )

    assert result["review_required"] is True
    assert "not proof of compliance" in result["note"]


def test_returns_no_evidence_when_search_finds_nothing():
    class EmptyKnowledgeBase:
        def search(self, query: str, top_k: int = 3) -> list[dict]:
            return []

    requirement = make_requirement(
        "The supplier must demonstrate secure API practices."
    )

    result = retrieve_evidence_for_requirement(
        requirement,
        EmptyKnowledgeBase(),
    )

    assert result["evidence_found"] is False
    assert result["evidence"] == []
    assert result["review_required"] is True


def test_rejects_empty_requirement():
    requirement = make_requirement("   ")

    with pytest.raises(ValueError, match="cannot be empty"):
        retrieve_evidence_for_requirement(
            requirement,
            FakeKnowledgeBase(),
        )
