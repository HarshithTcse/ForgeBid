
from pathlib import Path

import pymupdf


def extract_text_from_pdf(file_path: str | Path) -> str:
    """Extract text from a text-based PDF file."""

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("The input file must have a .pdf extension.")

    extracted_pages = []

    with pymupdf.open(path) as document:
        for page in document:
            page_text = page.get_text().strip()

            if page_text:
                extracted_pages.append(page_text)

    extracted_text = "\n\n".join(extracted_pages)

    if not extracted_text.strip():
        raise ValueError(
            "No text could be extracted. The PDF may be scanned "
            "or contain only images; OCR may be required."
        )

    return extracted_text
