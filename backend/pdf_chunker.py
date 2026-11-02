"""
pdf_chunker.py
--------------
Extract text from PDF files and split into searchable chunks.
Uses PyMuPDF (pymupdf) for reliable PDF text extraction.
"""

import re
from pathlib import Path

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract all text from a PDF file using PyMuPDF or pypdf."""
    try:
        import pymupdf

        doc = pymupdf.open(str(pdf_path))
        pages_text = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            if text and text.strip():
                pages_text.append(text.strip())
        doc.close()
        return "\n\n".join(pages_text)
    except ImportError:
        import pypdf

        reader = pypdf.PdfReader(str(pdf_path))
        pages_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text and text.strip():
                pages_text.append(text.strip())
        return "\n\n".join(pages_text)


def clean_pdf_text(text: str) -> str:
    """Clean extracted PDF text — fix line breaks, normalise whitespace."""
    # Remove page headers/footers that repeat
    text = re.sub(r"\n\s*\d+\s*\n", "\n", text)

    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if len(stripped) > 1:
            lines.append(stripped)

    return "\n".join(lines)


def _detect_section_label(
    text_block: str,
    active_section: str = "",
    active_chapter: str = "",
) -> tuple[str, str, str]:
    """Detect section / chapter headers from text, maintaining context across chunks.

    Returns: (label_for_this_chunk, new_active_section, new_active_chapter)
    """
    new_chapter = active_chapter
    new_section = active_section

    # Check for chapter header (e.g. "CHAPTER II\nINVENTIONS NOT PATENTABLE")
    chap_match = re.search(
        r"(?:^|\n)(CHAPTER\s+[IVXLCDM]+)\s*(?:\n|—|\s{2,})([A-Z\s]{3,50})?",
        text_block[:400],
    )
    if chap_match:
        chap_num = chap_match.group(1).strip()
        chap_name = (chap_match.group(2) or "").strip()
        if chap_name and not re.search(r"\.\s*\.\s*\.", chap_name):
            new_chapter = f"{chap_num}: {chap_name.title()}"
        else:
            new_chapter = chap_num
        new_section = new_chapter

    # Check for section header in statutory format:
    # e.g., "3. What are not inventions.—" or "Section 3(p)" or "84. Compulsory licences.—"
    sec_match = re.search(
        r"(?:^|\n)(\d+[A-Z]?)\.\s+([A-Z][^\n\.\—\-]{2,60})",
        text_block[:500],
    )
    if sec_match:
        sec_num = sec_match.group(1).strip()
        sec_title = sec_match.group(2).strip()
        # Ensure it's not a TOC line with dots
        if not re.search(r"\.\s*\.\s*\.", sec_title):
            new_section = f"Section {sec_num} — {sec_title}"

    # Also check explicit "Section \d+" pattern
    explicit_match = re.search(
        r"(Section\s+\d+[A-Z]?(?:\s*\([a-z0-9]+\))?)",
        text_block[:400],
    )
    if explicit_match and not sec_match:
        new_section = explicit_match.group(1).strip()

    label = new_section or new_chapter or "General"
    return label, new_section, new_chapter


def split_into_chunks(text: str) -> list[dict]:
    """Split text into overlapping chunks with persistent section labels."""
    chunks = []
    start = 0
    active_section = ""
    active_chapter = ""

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))

        # Try to break at a paragraph boundary
        if end < len(text):
            last_break = text.rfind("\n", start, end)
            if last_break > start + 300:
                end = last_break

        chunk_text = text[start:end].strip()

        if chunk_text and len(chunk_text) > 50:
            label, active_section, active_chapter = _detect_section_label(
                chunk_text,
                active_section=active_section,
                active_chapter=active_chapter,
            )
            chunks.append({
                "section_label": label,
                "content": chunk_text,
            })

        if end >= len(text):
            break

        start = max(end - CHUNK_OVERLAP, start + 1)

    return chunks


def chunk_pdf_file(pdf_path: Path) -> list[dict]:
    """Extract and chunk a PDF file. Returns list of {section_label, content}."""
    raw_text = extract_pdf_text(pdf_path)

    if not raw_text or len(raw_text) < 100:
        raise ValueError(f"Could not extract meaningful text from {pdf_path}")

    cleaned = clean_pdf_text(raw_text)
    return split_into_chunks(cleaned)
