
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

def test_unrelated_text_is_not_a_requirement():
    result = parse_rfp(
        "The project starts next Monday."
    )

    assert result.requirements == []


def test_extracts_multiple_evaluation_criteria():
    text = """
    Evaluation criteria: Technical quality 60%
    Evaluation criteria: Cost effectiveness 40%
    """

    result = parse_rfp(text)

    assert result.evaluation_criteria == [
        "Technical quality 60%",
        "Cost effectiveness 40%",
    ]

def test_mandatory_keywords_are_case_insensitive():
    text = """
    The supplier MUST provide support.
    The bidder Shall submit documentation.
    The vendor must maintain security.
    """

    result = parse_rfp(text)

    assert len(result.requirements) == 3
    assert all(r.mandatory for r in result.requirements)

def test_mandatory_and_optional_requirements_are_distinguished():
    text = """
    The supplier must provide technical support.
    Requirement: Provide a project overview.
    The bidder shall submit security documents.
    """

    result = parse_rfp(text)

    assert len(result.requirements) == 3
    assert result.requirements[0].mandatory is True
    assert result.requirements[1].mandatory is False
    assert result.requirements[2].mandatory is True

def test_requirement_categories_are_detected():
    text = """
    The supplier must implement security encryption.
    The supplier must provide technical support.
    The bidder shall submit project documentation.
    The supplier must explain the pricing structure.
    """

    result = parse_rfp(text)

    assert result.requirements[0].category == "security"
    assert result.requirements[1].category == "support"
    assert result.requirements[2].category == "documentation"
    assert result.requirements[3].category == "pricing"

def test_unrelated_requirement_gets_general_category():
    text = "The supplier must provide a colorful dashboard."

    result = parse_rfp(text)

    assert len(result.requirements) == 1
    assert result.requirements[0].category == "general"
