
def evaluate_bid_readiness(evidence_report: dict) -> dict:
    """
    Produce a preliminary bid recommendation from an evidence report.

    Missing evidence triggers review, not an automatic NO-GO decision.
    Candidate evidence is not proof of compliance.
    """
    requirements = evidence_report.get("requirements", [])

    issues = []
    mandatory_requirements = [
        item for item in requirements if item.get("mandatory", False)
    ]

    if not requirements:
        issues.append({
            "type": "NO_REQUIREMENTS",
            "severity": "HIGH",
            "message": "No requirements are available for evaluation.",
        })

    for item in mandatory_requirements:
        status = item.get("evidence_status")

        if status != "CANDIDATE_EVIDENCE_FOUND":
            issues.append({
                "type": "MANDATORY_EVIDENCE_GAP",
                "severity": "HIGH",
                "requirement_id": item.get("requirement_id"),
                "message": (
                    "No close evidence match was found for this mandatory "
                    "requirement. Verify company capability and source "
                    "documents before deciding."
                ),
            })

    for item in requirements:
        if item.get("review_required", True):
            # Evidence still requires human verification.
            continue

        issues.append({
            "type": "REVIEW_STATUS_UNEXPECTED",
            "severity": "MEDIUM",
            "requirement_id": item.get("requirement_id"),
            "message": "Verify the evidence review status.",
        })

    if not requirements or issues:
        recommendation = "NEEDS_REVIEW"
    else:
        recommendation = "PRELIMINARY_GO_CANDIDATE"

    return {
        "rfp_title": evidence_report.get("rfp_title", "Untitled RFP"),
        "recommendation": recommendation,
        "mandatory_requirement_count": len(mandatory_requirements),
        "requirements_reviewed": len(requirements),
        "issues": issues,
        "human_review_required": True,
        "limitations": [
            "Candidate evidence does not prove compliance.",
            "No close semantic match does not prove the company is incapable.",
            "Delivery feasibility, costs, staffing, deadlines, and contractual "
            "risks must be assessed before a final bid decision.",
        ],
    }
