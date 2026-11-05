import hashlib
from pathlib import Path

import requests

from database import get_connection

SOURCE_URL = (
    "https://www.ipindia.gov.in/writereaddata/Portal/IPOAct/"
    "1_113_1_The_Patents_Act__1970___incorporating_all_"
    "amendments_till_1-08-2024.pdf"
)

RAW_FILE_PATH = (
    Path(__file__).parent
    / "data"
    / "raw"
    / "patents_act_1970_2024.pdf"
)


def download_patents_act():
    response = requests.get(
        SOURCE_URL,
        headers={
            "User-Agent": "Ayurlex research prototype/0.1",
            "Accept": "application/pdf",
        },
        timeout=(20, 120),
    )
    response.raise_for_status()

    if not response.content.startswith(b"%PDF"):
        raise ValueError(
            "The official source did not return a PDF. "
            "No file was saved."
        )

    RAW_FILE_PATH.write_bytes(response.content)
    checksum = hashlib.sha256(response.content).hexdigest()

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE documents
            SET checksum = ?
            WHERE source_url = ?
            """,
            (checksum, SOURCE_URL),
        )
        connection.commit()

    print(f"Downloaded: {RAW_FILE_PATH.name}")
    print(f"File size: {len(response.content)} bytes")
    print(f"SHA-256: {checksum}")


if __name__ == "__main__":
    download_patents_act()