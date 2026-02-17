from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class QuoteItemDTO:
    id: str
    service_name: str
    unit: str
    quantity: int
    unit_price_cents: int
    adjustment_cents: int
    line_total_cents: int


@dataclass(frozen=True, slots=True)
class QuoteDetailsDTO:
    id: str
    customer_name: str
    status: str
    materials_included: bool
    total_sale_cents: int
    items: list[QuoteItemDTO]
