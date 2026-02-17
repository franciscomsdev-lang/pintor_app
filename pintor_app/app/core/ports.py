from __future__ import annotations
from typing import Protocol, Optional


class ServicesRepositoryPort(Protocol):
    def get_by_id(self, service_id: str):
        ...


class QuickQuotesRepositoryPort(Protocol):
    # Quotes
    def create_draft(self, customer_name: str, materials_included: bool = False, quote_id: Optional[str] = None) -> str:
        ...

    def get_by_id(self, quote_id: str):
        ...

    def list_history(self, status: Optional[str] = None, limit: int = 50):
        ...

    def update_status(self, quote_id: str, status: str) -> None:
        ...

    def update_notes(self, quote_id: str, notes_client: str, notes_internal: str = "") -> None:
        ...

    def set_totals(self, quote_id: str, subtotal_sale_cents: int, adjustments_cents: int, total_sale_cents: int) -> None:
        ...

    # Items
    def add_item(
        self,
        quote_id: str,
        service_name: str,
        unit: str,
        quantity: int,
        unit_price_cents: int,
        adjustment_cents: int = 0,
        description_client: str = "",
        item_id: Optional[str] = None,
    ) -> str:
        ...

    def list_items(self, quote_id: str):
        ...

    def get_quote_with_items(self, quote_id: str):
        ...
