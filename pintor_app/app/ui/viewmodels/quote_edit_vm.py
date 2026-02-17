from __future__ import annotations
from dataclasses import dataclass,field


@dataclass(slots=True)
class QuoteEditItemVM:
    item_id: str
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
class QuoteEditVM:
    is_loading: bool = True
    is_saving: bool = False
    error: str | None = None

    quote_id: str = ""
    customer_name: str = ""
    status: str = ""
    materials_included: bool = False
    total_sale_cents: int = 0
    total_sale_brl: str = ""


    items: list[QuoteEditItemVM] = field(default_factory=list)

    new_service_name: str = ""
    new_unit: str = ""
    new_quantity: str = "1"
    new_unit_price: str = ""
    new_adjustment: str = "0"
    form_error: str | None = None
    # no QuoteEditVM
    unit_locked: bool = True
    unit_price_locked: bool = True
    

