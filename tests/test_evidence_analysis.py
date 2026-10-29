
import pytest

from forgebid.evidence_analysis import analyze_rfp_evidence
from forgebid.models import Requirement, RFPDocument


class FakeKnowledgeBase:
    def search(self, query: str, top_k: int = 3) -> list[dict]:
        if "security" in query.lower():
            return [
                {
                    "text": "API input validation is documented.",
                    "source": "security_policy.md",
                    "chunk_number": 0,
                    "distance": 0.20,
                }
            ]

        return [
            {
                "text": "Unrelated sample content.",
                "source": "company_profile.md",
                "chunk_number": 0,
                "distance": 0.80,
            }
        ]


@pytest.fixture
def sample_rfp():
    return RFPDocument(
        title="Sample Software RFP",
        requirements=[
            Requirement(
                requirement_id="REQ-1",
                description="Security practices for API development",
                category="security",
                mandatory=True,
            ),
            Requirement(
                requirement_id="REQ-2",
                description="Provide a regional office",
                category="general",
                mandatory=False,
            ),
        ],
        evaluation_criteria=["Technical capability"],
    )


def test_analyzes_every_requirement(sample_rfp):
    result = analyze_rfp_evidence(sample_rfp, FakeKnowledgeBase())

    assert result["total_requirements"] == 2
    assert result["mandatory_requirements"] == 1
    assert result["optional_requirements"] == 1
    assert len(result["requirements"]) == 2


def test_identifies_candidate_evidence(sample_rfp):
    result = analyze_rfp_evidence(sample_rfp, FakeKnowledgeBase())

    first = result["requirements"][0]

    assert first["evidence_status"] == "CANDIDATE_EVIDENCE_FOUND"
    assert first["evidence"][0]["source"] == "security_policy.md"


def test_flags_no_close_match(sample_rfp):
    result = analyze_rfp_evidence(sample_rfp, FakeKnowledgeBase())

    second = result["requirements"][1]

    assert second["evidence_status"] == "NO_CLOSE_MATCH_FOUND"
    assert second["evidence"] == []
    assert second["review_required"] is True


def test_rejects_invalid_top_k(sample_rfp):
    with pytest.raises(ValueError, match="top_k"):
        analyze_rfp_evidence(
            sample_rfp,
            FakeKnowledgeBase(),
            top_k=0,
        )


def test_rejects_negative_distance_threshold(sample_rfp):
    with pytest.raises(ValueError, match="max_distance"):
        analyze_rfp_evidence(
            sample_rfp,
            FakeKnowledgeBase(),
            max_distance=-0.1,
        )
