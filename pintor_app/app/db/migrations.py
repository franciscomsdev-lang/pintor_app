from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Iterable, Tuple


Migration = Tuple[int, str]  # (version, sql)


def _ensure_migrations_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
          version INTEGER PRIMARY KEY,
          applied_at TEXT NOT NULL
        );
        """
    )


def _applied_versions(conn: sqlite3.Connection) -> set[int]:
    cur = conn.execute("SELECT version FROM schema_migrations;")
    return {int(r["version"]) for r in cur.fetchall()}


def _apply_migration(conn: sqlite3.Connection, version: int, sql: str) -> None:
    conn.executescript(sql)
    conn.execute(
        "INSERT INTO schema_migrations(version, applied_at) VALUES (?, ?);",
        (version, datetime.utcnow().isoformat()),
    )


def run_migrations(conn: sqlite3.Connection, migrations: Iterable[Migration]) -> None:
    _ensure_migrations_table(conn)
    applied = _applied_versions(conn)

    for version, sql in sorted(migrations, key=lambda x: x[0]):
        if version in applied:
            continue
        _apply_migration(conn, version, sql)

    conn.commit()


def get_migrations() -> list[Migration]:
    m001 = """
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS services (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      unit TEXT NOT NULL,
      default_unit_price_cents INTEGER NOT NULL DEFAULT 0,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_services_name ON services(name);

    CREATE TABLE IF NOT EXISTS quotes (
      id TEXT PRIMARY KEY,
      customer_name TEXT NOT NULL,
      status TEXT NOT NULL,
      materials_included INTEGER NOT NULL DEFAULT 0,
      notes_client TEXT NOT NULL DEFAULT '',
      notes_internal TEXT NOT NULL DEFAULT '',

      subtotal_sale_cents INTEGER NOT NULL DEFAULT 0,
      adjustments_cents INTEGER NOT NULL DEFAULT 0,
      total_sale_cents INTEGER NOT NULL DEFAULT 0,

      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_quotes_status_updated ON quotes(status, updated_at);

    CREATE TABLE IF NOT EXISTS quote_items (
      id TEXT PRIMARY KEY,
      quote_id TEXT NOT NULL,
      service_name TEXT NOT NULL,
      unit TEXT NOT NULL,
      quantity INTEGER NOT NULL,
      unit_price_cents INTEGER NOT NULL,
      adjustment_cents INTEGER NOT NULL DEFAULT 0,
      description_client TEXT NOT NULL DEFAULT '',

      FOREIGN KEY (quote_id) REFERENCES quotes(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_quote_items_quote ON quote_items(quote_id);
    """

    m002 = """
    PRAGMA foreign_keys = ON;

    ALTER TABLE quote_items
      ADD COLUMN quantity_thousandths INTEGER NOT NULL DEFAULT 0;

    UPDATE quote_items
      SET quantity_thousandths = quantity * 1000
      WHERE quantity_thousandths = 0;

    CREATE INDEX IF NOT EXISTS idx_quote_items_quote_qty
      ON quote_items(quote_id, quantity_thousandths);
    """

    return [
        (1, m001),
        (2, m002),
    ]

