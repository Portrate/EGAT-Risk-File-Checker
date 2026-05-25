import json
import os
import sqlite3
import sys
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path


def _db_path() -> Path:
    # Use a per-user writable location so a frozen .exe in Program Files can still write
    base = Path.home() / ".egat-file-checker"
    base.mkdir(parents=True, exist_ok=True)
    return base / "history.db"


DB_PATH = _db_path()


@contextmanager
def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                filename TEXT NOT NULL,
                model TEXT NOT NULL,
                total INTEGER NOT NULL,
                passed INTEGER NOT NULL,
                failed INTEGER NOT NULL,
                total_score REAL NOT NULL,
                passed_score REAL NOT NULL,
                similarity_score INTEGER NOT NULL,
                results_json TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_history_created_at ON history(created_at DESC)")


def save_history(
    filename: str,
    model: str,
    summary: dict,
    similarity_score: int,
    results: list,
) -> int:
    with _connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO history (
                created_at, filename, model,
                total, passed, failed,
                total_score, passed_score, similarity_score,
                results_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(timespec="seconds"),
                filename,
                model,
                int(summary.get("total", 0)),
                int(summary.get("passed", 0)),
                int(summary.get("failed", 0)),
                float(summary.get("total_score", 0)),
                float(summary.get("passed_score", 0)),
                int(similarity_score),
                json.dumps(results, ensure_ascii=False),
            ),
        )
        return cur.lastrowid


def list_history() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id, created_at, filename, model,
                   total, passed, failed,
                   total_score, passed_score, similarity_score
            FROM history
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]


def get_history(history_id: int) -> dict | None:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM history WHERE id = ?", (history_id,)).fetchone()
        if not row:
            return None
        item = dict(row)
        item["results"] = json.loads(item.pop("results_json"))
        item["summary"] = {
            "total": item["total"],
            "passed": item["passed"],
            "failed": item["failed"],
            "total_score": item["total_score"],
            "passed_score": item["passed_score"],
        }
        return item


def delete_history(history_id: int) -> bool:
    with _connect() as conn:
        cur = conn.execute("DELETE FROM history WHERE id = ?", (history_id,))
        return cur.rowcount > 0
