from __future__ import annotations


from typing import Optional


from pathlib import Path
import sqlite3
from typing import Union




def connect_sqlite(db_path: Union[str, Path]) -> sqlite3.Connection:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # timeout aumenta a tolerância antes de levantar "database is locked"
    conn = sqlite3.connect(db_path, timeout=30)

    # se você usa acesso por nome nas rows
    conn.row_factory = sqlite3.Row

    # pragmas para concorrência melhor em web
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")      # melhora concorrência
    conn.execute("PRAGMA synchronous = NORMAL;")    # ok p/ WAL
    conn.execute("PRAGMA busy_timeout = 30000;")    # 30s esperando lock

    return conn




def close_quietly(conn: Optional[sqlite3.Connection]) -> None:
    try:
        if conn is not None:
            conn.close()
    except Exception:
        pass
