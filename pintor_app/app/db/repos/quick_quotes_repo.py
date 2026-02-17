from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class QuoteRow:
    id: str
    customer_name: str
    status: str
    materials_included: int
    notes_client: str
    notes_internal: str
    subtotal_sale_cents: int
    adjustments_cents: int
    total_sale_cents: int
    created_at: str
    updated_at: str


@dataclass(frozen=True, slots=True)
class QuoteItemRow:
    id: str
    quote_id: str
    service_name: str
    unit: str
    quantity: int  # legado (compat)
    quantity_thousandths: int  # novo (fonte da verdade)
    unit_price_cents: int
    adjustment_cents: int
    description_client: str





class QuickQuotesRepo:
    """
    Repositório puro para o MVP de orçamentos rápidos.

    Importante:
    - aqui NÃO calcula totals (isso será domain/core depois).
    - aqui apenas persiste quote e itens.
    """

    def __init__(self, conn: sqlite3.Connection, now_fn=lambda: datetime.utcnow()) -> None:
        self.conn = conn
        self.now_fn = now_fn

    # -------- Quotes --------

    def create_draft(
        self,
        customer_name: str,
        materials_included: bool = False,
        quote_id: Optional[str] = None,
    ) -> str:
        now = self.now_fn().isoformat()
        qid = quote_id or str(uuid4())

        self.conn.execute(
            """
            INSERT INTO quotes (
              id, customer_name, status, materials_included,
              notes_client, notes_internal,
              subtotal_sale_cents, adjustments_cents, total_sale_cents,
              created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                qid,
                customer_name,
                "DRAFT",
                1 if materials_included else 0,
                "",
                "",
                0,
                0,
                0,
                now,
                now,
            ),
        )
        return qid

    def update_status(self, quote_id: str, status: str) -> None:
        now = self.now_fn().isoformat()
        cur = self.conn.execute(
            "UPDATE quotes SET status = ?, updated_at = ? WHERE id = ?;",
            (status, now, quote_id),
        )
        if cur.rowcount == 0:
            raise ValueError(f"Quote not found: {quote_id}")

    def update_notes(self, quote_id: str, notes_client: str, notes_internal: str = "") -> None:
        now = self.now_fn().isoformat()
        cur = self.conn.execute(
            """
            UPDATE quotes
               SET notes_client = ?, notes_internal = ?, updated_at = ?
             WHERE id = ?;
            """,
            (notes_client, notes_internal, now, quote_id),
        )
        if cur.rowcount == 0:
            raise ValueError(f"Quote not found: {quote_id}")

    def set_totals(
        self,
        quote_id: str,
        subtotal_sale_cents: int,
        adjustments_cents: int,
        total_sale_cents: int,
    ) -> None:
        """
        MVP: permitido setar totals como snapshot.
        O cálculo real virá do domain/core.
        """
        now = self.now_fn().isoformat()
        cur = self.conn.execute(
            """
            UPDATE quotes
               SET subtotal_sale_cents = ?,
                   adjustments_cents   = ?,
                   total_sale_cents    = ?,
                   updated_at          = ?
             WHERE id = ?;
            """,
            (int(subtotal_sale_cents), int(adjustments_cents), int(total_sale_cents), now, quote_id),
        )
        if cur.rowcount == 0:
            raise ValueError(f"Quote not found: {quote_id}")

    def get_by_id(self, quote_id: str) -> QuoteRow:
        cur = self.conn.execute(
            """
            SELECT id, customer_name, status, materials_included,
                   notes_client, notes_internal,
                   subtotal_sale_cents, adjustments_cents, total_sale_cents,
                   created_at, updated_at
              FROM quotes
             WHERE id = ?;
            """,
            (quote_id,),
        )
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"Quote not found: {quote_id}")

        return QuoteRow(
            id=row["id"],
            customer_name=row["customer_name"],
            status=row["status"],
            materials_included=int(row["materials_included"]),
            notes_client=row["notes_client"],
            notes_internal=row["notes_internal"],
            subtotal_sale_cents=int(row["subtotal_sale_cents"]),
            adjustments_cents=int(row["adjustments_cents"]),
            total_sale_cents=int(row["total_sale_cents"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def list_history(self, status: Optional[str] = None, limit: int = 50) -> list[QuoteRow]:
        if status:
            cur = self.conn.execute(
                """
                SELECT id, customer_name, status, materials_included,
                       notes_client, notes_internal,
                       subtotal_sale_cents, adjustments_cents, total_sale_cents,
                       created_at, updated_at
                  FROM quotes
                 WHERE status = ?
                 ORDER BY updated_at DESC
                 LIMIT ?;
                """,
                (status, int(limit)),
            )
        else:
            cur = self.conn.execute(
                """
                SELECT id, customer_name, status, materials_included,
                       notes_client, notes_internal,
                       subtotal_sale_cents, adjustments_cents, total_sale_cents,
                       created_at, updated_at
                  FROM quotes
                 ORDER BY updated_at DESC
                 LIMIT ?;
                """,
                (int(limit),),
            )

        rows = cur.fetchall()
        return [
            QuoteRow(
                id=r["id"],
                customer_name=r["customer_name"],
                status=r["status"],
                materials_included=int(r["materials_included"]),
                notes_client=r["notes_client"],
                notes_internal=r["notes_internal"],
                subtotal_sale_cents=int(r["subtotal_sale_cents"]),
                adjustments_cents=int(r["adjustments_cents"]),
                total_sale_cents=int(r["total_sale_cents"]),
                created_at=r["created_at"],
                updated_at=r["updated_at"],
            )
            for r in rows
        ]

    # -------- Quote Items --------

    def add_item(
        self,
        quote_id: str,
        service_name: str,
        unit: str,
        quantity_thousandths: int,
        unit_price_cents: int,
        adjustment_cents: int = 0,
        description_client: str = "",
        item_id: Optional[str] = None,
    ) -> str:
        iid = item_id or str(uuid4())
        quantity_int = int(int(quantity_thousandths) // 1000)  # legado

        self.conn.execute(
            """
            INSERT INTO quote_items (
            id, quote_id, service_name, unit,
            quantity, quantity_thousandths,
            unit_price_cents, adjustment_cents, description_client
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                iid,
                quote_id,
                service_name,
                unit,
                quantity_int,
                int(quantity_thousandths),
                int(unit_price_cents),
                int(adjustment_cents),
                description_client,
            ),
        )

        now = self.now_fn().isoformat()
        self.conn.execute("UPDATE quotes SET updated_at = ? WHERE id = ?;", (now, quote_id))
        return iid


    def list_items(self, quote_id: str) -> list[QuoteItemRow]:
        cur = self.conn.execute(
            """
            SELECT id, quote_id, service_name, unit,
                quantity,
                quantity_thousandths,
                unit_price_cents, adjustment_cents, description_client
            FROM quote_items
            WHERE quote_id = ?
            ORDER BY rowid ASC;

            """,
            (quote_id,),
        )
        rows = cur.fetchall()
        return [
            QuoteItemRow(
                id=r["id"],
                quote_id=r["quote_id"],
                service_name=r["service_name"],
                unit=r["unit"],
                quantity=int(r["quantity"]),
                quantity_thousandths=int(r["quantity_thousandths"]),
                unit_price_cents=int(r["unit_price_cents"]),
                adjustment_cents=int(r["adjustment_cents"]),
                description_client=r["description_client"],
            )
            for r in rows
        ]




    def delete_item(self, item_id: str) -> None:
        # encontra quote_id para tocar updated_at
        cur = self.conn.execute("SELECT quote_id FROM quote_items WHERE id = ?;", (item_id,))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"Quote item not found: {item_id}")

        quote_id = row["quote_id"]
        self.conn.execute("DELETE FROM quote_items WHERE id = ?;", (item_id,))

        now = self.now_fn().isoformat()
        self.conn.execute("UPDATE quotes SET updated_at = ? WHERE id = ?;", (now, quote_id))

    def get_quote_with_items(self, quote_id: str) -> tuple[QuoteRow, list[QuoteItemRow]]:
        quote = self.get_by_id(quote_id)
        items = self.list_items(quote_id)
        return quote, items
