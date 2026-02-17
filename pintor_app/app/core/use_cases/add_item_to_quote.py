from __future__ import annotations
from dataclasses import dataclass

from app.core.errors import ValidationError, NotFoundError
from app.core.ports import QuickQuotesRepositoryPort
from app.domain.money import Money
from app.domain.models import QuoteItem, calculate_quote_totals
from decimal import Decimal
from app.domain.quantity import Quantity



@dataclass(frozen=True, slots=True)
class AddItemToQuoteInput:
    quote_id: str
    service_name: str
    unit: str  
    quantity: Decimal             # M2, DAY, ROOM, UNIT
    unit_price_cents: int
    adjustment_cents: int = 0
    description_client: str = ""


class AddItemToQuote:
    def __init__(self, quotes_repo: QuickQuotesRepositoryPort) -> None:
        self.quotes_repo = quotes_repo

    def execute(self, inp: AddItemToQuoteInput) -> str:
        if not (inp.quote_id or "").strip():
            raise ValidationError("quote_id é obrigatório.")

        if (inp.service_name or "").strip() == "":
            raise ValidationError("Nome do serviço é obrigatório.")

        if inp.quantity <= 0:
            raise ValidationError("Quantidade deve ser maior que zero.")

        if inp.unit_price_cents < 0:
            raise ValidationError("Preço unitário inválido.")

        # garante que quote existe
        try:
            self.quotes_repo.get_by_id(inp.quote_id)
        except ValueError:
            raise NotFoundError("Orçamento não encontrado.")

        # adiciona item no repositório
        qty_dec = inp.quantity if isinstance(inp.quantity, Decimal) else Decimal(str(inp.quantity))
        qty = Quantity.from_decimal(qty_dec, unit=inp.unit)


        item_id = self.quotes_repo.add_item(
            quote_id=inp.quote_id,
            service_name=inp.service_name.strip(),
            unit=inp.unit,
            quantity_thousandths=qty.to_thousandths(),
            unit_price_cents=int(inp.unit_price_cents),
            adjustment_cents=int(inp.adjustment_cents),
            description_client=inp.description_client or "",
        )

        # recalcula totals a partir dos itens persistidos
        item_rows = self.quotes_repo.list_items(inp.quote_id)

        domain_items = [
            QuoteItem(
                id=r.id,
                quote_id=r.quote_id,
                service_name=r.service_name,
                unit=r.unit,
                quantity=Quantity.from_thousandths(int(r.quantity_thousandths), unit=r.unit),
                unit_price=Money(int(r.unit_price_cents)),
                adjustment=Money(int(r.adjustment_cents)),
                description_client=r.description_client,
            )
            for r in item_rows
        ]



        totals = calculate_quote_totals(domain_items)

        self.quotes_repo.set_totals(
            quote_id=inp.quote_id,
            subtotal_sale_cents=totals.subtotal_sale.cents,
            adjustments_cents=totals.adjustments.cents,
            total_sale_cents=totals.total_sale.cents,
        )

        return item_id
