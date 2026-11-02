from database import get_connection


OFFICIAL_SOURCES = [
    {
        "title": "The Patents Act, 1970 - India Code",
        "source_url": (
            "https://www.indiacode.nic.in/"
            "handle/123456789/1392"
        ),
        "jurisdiction": "india",
        "effective_date": "1978-04-01",
    },
    {
        "title": (
            "The Patents Act, 1970 - IP India "
            "(amendments incorporated till 2024-08-01)"
        ),
        "source_url": (
            "https://ipindia.gov.in/writereaddata/"
            "Portal/IPOAct/1_113_1_The_Patents_Act__1970___"
            "incorporating_all_amendments_till_1-08-2024.pdf"
        ),
        "jurisdiction": "india",
        "effective_date": "2024-08-01",
    },
]


def seed_official_sources():
    with get_connection() as connection:
        for source in OFFICIAL_SOURCES:
            connection.execute(
                """
                INSERT OR IGNORE INTO documents (
                    title,
                    source_url,
                    jurisdiction,
                    effective_date
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    source["title"],
                    source["source_url"],
                    source["jurisdiction"],
                    source["effective_date"],
                ),
            )

        connection.commit()