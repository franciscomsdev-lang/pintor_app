from dataclasses import dataclass

@dataclass(slots=True)
class QuoteItemVM:
    service_name: str
    unit: str
    quantity: int
    unit_price_cents: int
    adjustment_cents: int
    line_total_cents: int

    unit_price_brl: str = ""
    adjustment_brl: str = ""
    line_total_brl: str = ""

@dataclass(slots=True)
class QuoteDetailsVM:
    is_loading: bool = True
    error: str | None = None

    quote_id: str = ""
    customer_name: str = ""
    status: str = ""
    materials_included: bool = False

    total_sale_cents: int = 0
    total_sale_brl: str = ""

    items: list[QuoteItemVM] = None  # type: ignore
