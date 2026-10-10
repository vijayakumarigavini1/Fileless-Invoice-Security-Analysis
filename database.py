import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent / "fileless_invoice.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module TEXT NOT NULL,
                status TEXT NOT NULL,
                output TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_result(module, status, output):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO analysis_history (module, status, output)
            VALUES (?, ?, ?)
            """,
            (module, status, output),
        )
        return cursor.lastrowid


def get_history(limit=50):
    limit = max(1, min(int(limit), 200))

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, module, status, output, created_at
            FROM analysis_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_result(result_id):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, module, status, output, created_at
            FROM analysis_history
            WHERE id = ?
            """,
            (result_id,),
        ).fetchone()

    return dict(row) if row else None