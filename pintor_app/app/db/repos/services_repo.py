from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class ServiceRow:
    id: str
    name: str
    unit: str  # M2, DAY, ROOM, UNIT
    default_unit_price_cents: int
    created_at: str
    updated_at: str


class ServicesRepo:
    """
    Repositório puro (SQLite):
    - CRUD básico de services
    - Sem regra de negócio
    """

    def __init__(self, conn: sqlite3.Connection, now_fn=lambda: datetime.utcnow()) -> None:
        self.conn = conn
        self.now_fn = now_fn

    def create(
        self,
        name: str,
        unit: str,
        default_unit_price_cents: int = 0,
        service_id: Optional[str] = None,
    ) -> str:
        now = self.now_fn().isoformat()
        sid = service_id or str(uuid4())

        self.conn.execute(
            """
            INSERT INTO services (id, name, unit, default_unit_price_cents, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (sid, name, unit, int(default_unit_price_cents), now, now),
        )
        return sid

    def update_price(self, service_id: str, default_unit_price_cents: int) -> None:
        now = self.now_fn().isoformat()
        cur = self.conn.execute(
            """
            UPDATE services
               SET default_unit_price_cents = ?, updated_at = ?
             WHERE id = ?;
            """,
            (int(default_unit_price_cents), now, service_id),
        )
        if cur.rowcount == 0:
            raise ValueError(f"Service not found: {service_id}")

    def get_by_id(self, service_id: str) -> ServiceRow:
        cur = self.conn.execute(
            """
            SELECT id, name, unit, default_unit_price_cents, created_at, updated_at
              FROM services
             WHERE id = ?;
            """,
            (service_id,),
        )
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"Service not found: {service_id}")
        return ServiceRow(
            id=row["id"],
            name=row["name"],
            unit=row["unit"],
            default_unit_price_cents=int(row["default_unit_price_cents"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def list_all(self) -> list[ServiceRow]:
        cur = self.conn.execute(
            """
            SELECT id, name, unit, default_unit_price_cents, created_at, updated_at
              FROM services
             ORDER BY name COLLATE NOCASE ASC;
            """
        )
        rows = cur.fetchall()
        return [
            ServiceRow(
                id=r["id"],
                name=r["name"],
                unit=r["unit"],
                default_unit_price_cents=int(r["default_unit_price_cents"]),
                created_at=r["created_at"],
                updated_at=r["updated_at"],
            )
            for r in rows
        ]

    def delete(self, service_id: str) -> None:
        cur = self.conn.execute("DELETE FROM services WHERE id = ?;", (service_id,))
        if cur.rowcount == 0:
            raise ValueError(f"Service not found: {service_id}")

    def upsert_many(self, services: Iterable[tuple[str, str, str, int]]) -> None:
        """
        Utilitário para seed:
        services: (id, name, unit, default_unit_price_cents)
        """
        now = self.now_fn().isoformat()
        self.conn.executemany(
            """
            INSERT INTO services (id, name, unit, default_unit_price_cents, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              name = excluded.name,
              unit = excluded.unit,
              default_unit_price_cents = excluded.default_unit_price_cents,
              updated_at = excluded.updated_at;
            """,
            [(sid, name, unit, int(price), now, now) for sid, name, unit, price in services],
        )
