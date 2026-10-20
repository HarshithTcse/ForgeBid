
import re

from forgebid.models import Requirement, RFPDocument


def parse_rfp(text: str, title: str = "Untitled RFP") -> RFPDocument:
    """Extract basic requirements and evaluation criteria from RFP text."""

    if not text or not text.strip():
        raise ValueError("RFP text cannot be empty.")

    requirements = []
    criteria = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        if re.match(r"evaluation criteria\s*:", line, re.IGNORECASE):
            value = line.split(":", 1)[1].strip()
            if value:
                criteria.append(value)
            continue

        mandatory = bool(
            re.search(r"\b(must|required|shall)\b", line, re.IGNORECASE)
        )

        if mandatory or re.match(
            r"requirement\s*:", line, re.IGNORECASE
        ):
            description = re.sub(
                r"^requirement\s*:\s*",
                "",
                line,
                flags=re.IGNORECASE,
            )

            requirements.append(
                Requirement(
                    requirement_id=f"REQ-{len(requirements) + 1:03}",
                    description=description,
                    category="general",
                    mandatory=mandatory,
                )
            )

    return RFPDocument(
        title=title,
        requirements=requirements,
        evaluation_criteria=criteria,
    )
