
from forgebid.knowledge_base import CompanyKnowledgeBase
from forgebid.models import Requirement


def retrieve_evidence_for_requirement(
    requirement: Requirement,
    knowledge_base: CompanyKnowledgeBase,
    top_k: int = 3,
) -> dict:
    """Retrieve company evidence relevant to an RFP requirement."""

    if not requirement.description.strip():
        raise ValueError("Requirement description cannot be empty.")

    results = knowledge_base.search(
        query=requirement.description,
        top_k=top_k,
    )

    evidence = []

    for result in results:
        evidence.append(
            {
                "text": result["text"],
                "source": result["source"],
                "chunk_number": result["chunk_number"],
                "distance": result["distance"],
            }
        )

    return {
        "requirement_id": requirement.requirement_id,
        "requirement": requirement.description,
        "category": requirement.category,
        "mandatory": requirement.mandatory,
        "evidence_found": bool(evidence),
        "evidence": evidence,
        "review_required": True,
        "note": (
            "Retrieved text is supporting material, not proof of compliance. "
            "A human reviewer must verify the source and its applicability."
        ),
    }
