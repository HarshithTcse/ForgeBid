
import pytest

from forgebid.parser import parse_rfp


def test_extracts_mandatory_requirements():
    text = """
    The supplier must provide technical support.
    The bidder shall submit security documentation.
    """

    result = parse_rfp(text, "Support RFP")

    assert result.title == "Support RFP"
    assert len(result.requirements) == 2
    assert all(r.mandatory for r in result.requirements)
    assert result.requirements[0].requirement_id == "REQ-001"


def test_extracts_evaluation_criteria():
    result = parse_rfp(
        "Evaluation criteria: Technical quality 60%"
    )

    assert result.evaluation_criteria == [
        "Technical quality 60%"
    ]


def test_empty_input_is_rejected():
    with pytest.raises(ValueError, match="cannot be empty"):
        parse_rfp("   ")


def test_optional_requirement_is_not_mandatory():
    result = parse_rfp(
        "Requirement: Provide a project overview."
    )

    assert len(result.requirements) == 1
    assert result.requirements[0].mandatory is False
