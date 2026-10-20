
import pymupdf
import pytest
from forgebid.parser import parse_rfp_pdf

from forgebid.pdf_reader import extract_text_from_pdf


def create_test_pdf(path, text):
    with pymupdf.open() as document:
        page = document.new_page()
        page.insert_text((72, 72), text)
        document.save(path)


def test_extracts_text_from_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    create_test_pdf(pdf_path, "The supplier must provide technical support.")

    result = extract_text_from_pdf(pdf_path)

    assert "technical support" in result


def test_missing_pdf_raises_error(tmp_path):
    missing_path = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf(missing_path)


def test_non_pdf_file_is_rejected(tmp_path):
    text_path = tmp_path / "sample.txt"
    text_path.write_text("This is not a PDF.", encoding="utf-8")

    with pytest.raises(ValueError, match="pdf extension"):
        extract_text_from_pdf(text_path)


def test_pdf_without_extractable_text_raises_error(tmp_path):
    pdf_path = tmp_path / "empty.pdf"

    with pymupdf.open() as document:
        document.new_page()
        document.save(pdf_path)

    with pytest.raises(ValueError, match="No text could be extracted"):
        extract_text_from_pdf(pdf_path)


def test_parse_rfp_pdf_end_to_end(tmp_path):
    pdf_path = tmp_path / "support_rfp.pdf"

    create_test_pdf(
        pdf_path,
        "The supplier must provide technical support.",
    )

    result = parse_rfp_pdf(pdf_path)

    assert result.title == "support rfp"
    assert len(result.requirements) == 1
    assert result.requirements[0].mandatory is True
    assert result.requirements[0].category == "support"
