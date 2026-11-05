import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DATABASE_PATH = DATA_DIR / "ayurlex.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    DATA_DIR.mkdir(exist_ok=True)

    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                source_url TEXT NOT NULL UNIQUE,
                jurisdiction TEXT NOT NULL,
                effective_date TEXT,
                checksum TEXT,
                ingested_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                section_label TEXT NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
        """)

        # FTS5 virtual table for fast full-text search with BM25 ranking.
        # We use content-sync so FTS stays in step with the chunks table.
        connection.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                section_label,
                content,
                content='chunks',
                content_rowid='id',
                tokenize='porter unicode61'
            )
        """)

        # Triggers to keep FTS5 in sync when chunks are inserted or deleted.
        connection.executescript("""
            CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
                INSERT INTO chunks_fts(rowid, section_label, content)
                VALUES (new.id, new.section_label, new.content);
            END;

            CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
                INSERT INTO chunks_fts(chunks_fts, rowid, section_label, content)
                VALUES ('delete', old.id, old.section_label, old.content);
            END;

            CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
                INSERT INTO chunks_fts(chunks_fts, rowid, section_label, content)
                VALUES ('delete', old.id, old.section_label, old.content);
                INSERT INTO chunks_fts(rowid, section_label, content)
                VALUES (new.id, new.section_label, new.content);
            END;
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.commit()


def rebuild_fts_index():
    """Rebuild the FTS5 index from the current chunks table.

    Call this after bulk-inserting chunks without triggers (e.g. during
    the initial corpus seed).
    """
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO chunks_fts(chunks_fts) VALUES('rebuild')"
        )
        connection.commit()


def list_documents():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                title,
                source_url,
                jurisdiction,
                effective_date,
                ingested_at
            FROM documents
            ORDER BY id
            """
        ).fetchall()

    return [dict(row) for row in rows]