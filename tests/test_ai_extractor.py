
import pytest
from pydantic import ValidationError

from forgebid.models import RFPDocument
from forgebid.ai_extractor import extract_rfp_with_ai


def test_rfp_document_accepts_valid_data():
    data = {
        "title": "College Website Development",
        "submission_deadline": None,
        "requirements": [
            {
                "requirement_id": "REQ-001",
                "description": "The website must use HTTPS encryption.",
                "category": "security",
                "mandatory": True,
            }
        ],
        "evaluation_criteria": ["Technical quality"],
    }

    document = RFPDocument.model_validate(data)

    assert document.title == "College Website Development"
    assert len(document.requirements) == 1
    assert document.requirements[0].category == "security"


def test_rfp_document_rejects_missing_title():
    with pytest.raises(ValidationError):
        RFPDocument.model_validate({
            "requirements": [],
            "evaluation_criteria": [],
        })


def test_ai_extractor_rejects_empty_input():
    with pytest.raises(ValueError, match="cannot be empty"):
        extract_rfp_with_ai("   ")
