from __future__ import annotations
from dataclasses import dataclass
from app.domain.money import Money


from app.domain.quantity import Quantity


@dataclass(frozen=True, slots=True)
class QuoteItem:
    id: str
    quote_id: str
    service_name: str
    unit: str
    quantity: Quantity
    unit_price: Money
    adjustment: Money = Money(0)
    description_client: str = ""

    def line_total(self) -> Money:
        return self.unit_price.mul_decimal(self.quantity.value) + self.adjustment



@dataclass(frozen=True, slots=True)
class QuoteTotals:
    subtotal_sale: Money
    adjustments: Money
    total_sale: Money


def calculate_quote_totals(items: list[QuoteItem]) -> QuoteTotals:
    subtotal = Money(0)
    adjustments = Money(0)

    for it in items:
        subtotal += it.unit_price.mul_decimal(it.quantity.value)



    total = subtotal + adjustments
    return QuoteTotals(subtotal_sale=subtotal, adjustments=adjustments, total_sale=total)

