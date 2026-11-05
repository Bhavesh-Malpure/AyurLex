import hashlib
from pathlib import Path

from connectors.website_connector import fetch_public_source
from database import get_connection

RAW_DIRECTORY = Path(__file__).parent / "data" / "raw"


def get_file_extension(content_type: str) -> str:
    normalized_type = content_type.lower()

    if "pdf" in normalized_type:
        return ".pdf"

    if "html" in normalized_type:
        return ".html"

    return ".bin"


def ingest_source(
    title: str,
    source_url: str,
    jurisdiction: str,
) -> dict:
    fetched_source = fetch_public_source(source_url)

    RAW_DIRECTORY.mkdir(exist_ok=True)

    checksum = hashlib.sha256(
        fetched_source.content
    ).hexdigest()

    file_extension = get_file_extension(
        fetched_source.content_type
    )

    file_name = f"source_{checksum[:16]}{file_extension}"
    raw_file_path = RAW_DIRECTORY / file_name

    raw_file_path.write_bytes(fetched_source.content)

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO documents (
                title,
                source_url,
                jurisdiction,
                checksum
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT(source_url)
            DO UPDATE SET
                title = excluded.title,
                jurisdiction = excluded.jurisdiction,
                checksum = excluded.checksum,
                ingested_at = CURRENT_TIMESTAMP
            """,
            (
                title,
                source_url,
                jurisdiction,
                checksum,
            ),
        )

        document = connection.execute(
            """
            SELECT id, title, source_url, jurisdiction, checksum
            FROM documents
            WHERE source_url = ?
            """,
            (source_url,),
        ).fetchone()

        connection.commit()

    return {
        "document_id": document["id"],
        "title": document["title"],
        "source_url": document["source_url"],
        "final_url": fetched_source.final_url,
        "content_type": fetched_source.content_type,
        "raw_file": str(raw_file_path),
        "checksum": document["checksum"],
    }