from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional


def connect_sqlite(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # pragmas úteis e seguros
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")

    return conn


def close_quietly(conn: Optional[sqlite3.Connection]) -> None:
    try:
        if conn is not None:
            conn.close()
    except Exception:
        pass
