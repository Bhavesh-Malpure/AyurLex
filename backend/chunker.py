import re
from pathlib import Path

from bs4 import BeautifulSoup

from database import get_connection

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200
RAW_DIRECTORY = Path(__file__).parent / "data" / "raw"

REMOVE_TAGS = [
    "script",
    "style",
    "nav",
    "footer",
    "header",
    "aside",
    "form",
    "noscript",
    "svg",
]

MAIN_CONTENT_SELECTORS = [
    "main",
    "article",
    "[role='main']",
    "#main-content",
    "#main",
    "#content",
    ".main-content",
    ".main",
    ".content",
    ".article-content",
    ".entry-content",
]


def clean_text(text: str) -> str:
    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in text.splitlines()
    ]

    useful_lines = [
        line
        for line in lines
        if len(line) > 1
    ]

    return "\n".join(useful_lines)


def find_main_content(soup: BeautifulSoup):
    for selector in MAIN_CONTENT_SELECTORS:
        content = soup.select_one(selector)

        if content is not None:
            return content

    return soup.body or soup


def extract_html_text(raw_file_path: Path) -> str:
    html_content = raw_file_path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    soup = BeautifulSoup(
        html_content,
        "html.parser",
    )

    for tag in soup(REMOVE_TAGS):
        tag.decompose()

    main_content = find_main_content(soup)

    for tag in main_content.find_all(
        ["nav", "footer", "header", "aside", "form"]
    ):
        tag.decompose()

    return clean_text(
        main_content.get_text(separator="\n")
    )


def split_into_chunks(text: str) -> list[str]:
    chunks = []
    start = 0

    while start < len(text):
        end = min(
            start + CHUNK_SIZE,
            len(text),
        )

        if end < len(text):
            last_break = text.rfind(
                "\n",
                start,
                end,
            )

            if last_break > start + 300:
                end = last_break

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = max(
            end - CHUNK_OVERLAP,
            start + 1,
        )

    return chunks


def chunk_html_document(
    document_id: int,
    raw_file_path: Path,
) -> int:
    text = extract_html_text(raw_file_path)

    if not text:
        raise ValueError(
            "No readable main content was extracted "
            "from the HTML source."
        )

    chunks = split_into_chunks(text)

    with get_connection() as connection:
        connection.execute(
            "DELETE FROM chunks WHERE document_id = ?",
            (document_id,),
        )

        for index, chunk in enumerate(
            chunks,
            start=1,
        ):
            connection.execute(
                """
                INSERT INTO chunks (
                    document_id,
                    section_label,
                    content
                )
                VALUES (?, ?, ?)
                """,
                (
                    document_id,
                    f"Chunk {index}",
                    chunk,
                ),
            )

        connection.commit()

    return len(chunks)


def chunk_document_by_id(document_id: int) -> int:
    with get_connection() as connection:
        document = connection.execute(
            """
            SELECT checksum
            FROM documents
            WHERE id = ?
            """,
            (document_id,),
        ).fetchone()

    if document is None:
        raise ValueError(
            "Document ID was not found."
        )

    checksum = document["checksum"]

    if not checksum:
        raise ValueError(
            "This document has no downloaded source file."
        )

    matching_files = list(
        RAW_DIRECTORY.glob(
            f"source_{checksum[:16]}.*"
        )
    )

    if not matching_files:
        raise FileNotFoundError(
            "No matching raw file was found for "
            "this document."
        )

    raw_file_path = matching_files[0]

    if raw_file_path.suffix.lower() != ".html":
        raise ValueError(
            "This chunker currently supports HTML "
            "files only."
        )

    return chunk_html_document(
        document_id=document_id,
        raw_file_path=raw_file_path,
    )