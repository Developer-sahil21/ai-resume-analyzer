# modules/resume_parser.py
# Extract plain text from PDF files (via pdfplumber) or raw text input.

import pdfplumber
import re
from io import BytesIO


def parse_pdf(file_bytes: bytes) -> str:
    """
    Extract and return all text from a PDF supplied as raw bytes.
    Raises ValueError if the PDF is empty or unreadable.
    """
    text_parts = []

    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        if not pdf.pages:
            raise ValueError("PDF has no pages.")

        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

    full_text = "\n".join(text_parts).strip()

    if not full_text:
        raise ValueError("Could not extract text from PDF. "
                         "The file may be image-only (scanned). "
                         "Please paste your resume as plain text instead.")
    return full_text


def clean_text(text: str) -> str:
    """
    Light sanitisation:
    - Normalise Unicode dashes / quotes
    - Collapse excessive blank lines
    - Strip leading/trailing whitespace
    """
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text_from_upload(file_storage) -> str:
    """
    Accept a Flask FileStorage object.
    Supports .pdf and plain-text files (.txt, .doc treated as text).
    Returns cleaned plain text.
    """
    filename = file_storage.filename.lower()
    raw_bytes = file_storage.read()

    if not raw_bytes:
        raise ValueError("Uploaded file is empty.")

    if filename.endswith(".pdf"):
        text = parse_pdf(raw_bytes)
    else:
        # Assume UTF-8 plain text; fall back to latin-1
        try:
            text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = raw_bytes.decode("latin-1")

    return clean_text(text)
