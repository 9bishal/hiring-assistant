"""
tools/pdf_parser.py
===================
Parses PDF resumes into plain text using PyMuPDF.

How to explain to HR:
  "Resumes come in as PDFs. PyMuPDF extracts the raw text
   page by page. We clean it and pass it to the agents.
   No OCR needed for standard PDFs — it's fast and accurate."
"""

import fitz   # PyMuPDF


def parse_pdf(file_bytes: bytes) -> str:
    """
    Extract all text from a PDF file given its raw bytes.

    Args:
        file_bytes: raw bytes of the PDF file

    Returns:
        Cleaned plain text string
    """
    doc  = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""

    for page in doc:
        text += page.get_text()

    doc.close()

    # Basic cleanup — remove excessive whitespace
    lines   = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned = "\n".join(lines)

    return cleaned


def parse_pdf_file(filepath: str) -> str:
    """Parse a PDF from a local file path."""
    with open(filepath, "rb") as f:
        return parse_pdf(f.read())
