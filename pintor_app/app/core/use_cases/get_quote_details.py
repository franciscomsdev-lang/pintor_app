from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from app.core.dtos import QuoteDetailsDTO, QuoteItemDTO
from app.core.errors import NotFoundError
from app.core.ports import QuickQuotesRepositoryPort

class GetQuoteDetails:
    def __init__(self, quotes_repo: QuickQuotesRepositoryPort) -> None:
        self.quotes_repo = quotes_repo

    def execute(self, quote_id: str) -> QuoteDetailsDTO:
        try:
            quote, items = self.quotes_repo.get_quote_with_items(quote_id)
        except ValueError:
            raise NotFoundError("Orçamento não encontrado.")

        item_dtos: list[QuoteItemDTO] = []
        for it in items:
            unit_price_cents = int(it.unit_price_cents)
            adjustment_cents = int(it.adjustment_cents)

            # aceita tanto quantity antigo quanto quantity_thousandths novo
            qty_thousandths = getattr(it, "quantity_thousandths", None)
            if qty_thousandths is None:
                qty_thousandths = int(getattr(it, "quantity")) * 1000

            # cálculo correto em cents usando Decimal
            raw = Decimal(unit_price_cents) * (Decimal(int(qty_thousandths)) / Decimal(1000))
            line_subtotal_cents = int(raw.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
            line_total = line_subtotal_cents + adjustment_cents

            # para exibir no DTO, manter compatibilidade inteira
            # valor decimal real para exibição
            qty_thousandths = getattr(it, "quantity_thousandths", None)

            if qty_thousandths is None:
                # legado: quantity inteiro
                display_quantity = int(getattr(it, "quantity"))
            else:
                if it.unit == "M2":
                    display_quantity = float(Decimal(int(qty_thousandths)) / Decimal(1000))
                else:
                    display_quantity = int(int(qty_thousandths) // 1000)

            item_dtos.append(
                QuoteItemDTO(
                    id=it.id,
                    service_name=it.service_name,
                    unit=it.unit,
                    quantity=display_quantity,
                    unit_price_cents=unit_price_cents,
                    adjustment_cents=adjustment_cents,
                    line_total_cents=line_total,
                )
            )

        return QuoteDetailsDTO(
            id=quote.id,
            customer_name=quote.customer_name,
            status=quote.status,
            materials_included=bool(quote.materials_included),
            total_sale_cents=int(quote.total_sale_cents),
            items=item_dtos,
        )
