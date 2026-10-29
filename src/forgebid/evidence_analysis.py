
from forgebid.evidence_retrieval import retrieve_evidence_for_requirement
from forgebid.knowledge_base import CompanyKnowledgeBase
from forgebid.models import RFPDocument


# Initial tuning value, not a validated compliance threshold.
DEFAULT_MAX_DISTANCE = 0.45


def analyze_rfp_evidence(
    rfp: RFPDocument,
    knowledge_base: CompanyKnowledgeBase,
    top_k: int = 3,
    max_distance: float = DEFAULT_MAX_DISTANCE,
) -> dict:
    """Retrieve and organize candidate evidence for every RFP requirement."""

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    if max_distance < 0:
        raise ValueError("max_distance cannot be negative.")

    requirement_results = []

    for requirement in rfp.requirements:
        result = retrieve_evidence_for_requirement(
            requirement=requirement,
            knowledge_base=knowledge_base,
            top_k=top_k,
        )

        # Keep only closer matches as candidate evidence.
        # Distance is a retrieval signal, not proof of compliance.
        candidate_evidence = [
            item
            for item in result["evidence"]
            if item["distance"] <= max_distance
        ]

        if candidate_evidence:
            evidence_status = "CANDIDATE_EVIDENCE_FOUND"
        else:
            evidence_status = "NO_CLOSE_MATCH_FOUND"

        requirement_results.append(
            {
                "requirement_id": requirement.requirement_id,
                "requirement": requirement.description,
                "category": requirement.category,
                "mandatory": requirement.mandatory,
                "evidence_status": evidence_status,
                "evidence": candidate_evidence,
                "review_required": True,
            }
        )

    mandatory_count = sum(
        1 for item in rfp.requirements if item.mandatory
    )

    return {
        "rfp_title": rfp.title,
        "total_requirements": len(rfp.requirements),
        "mandatory_requirements": mandatory_count,
        "optional_requirements": len(rfp.requirements) - mandatory_count,
        "requirements": requirement_results,
        "review_required": True,
        "disclaimer": (
            "Similarity is not proof of compliance. The distance threshold "
            "is provisional and must be calibrated. Human reviewers must "
            "verify evidence against the original RFP and trusted company "
            "documents."
        ),
    }
