from __future__ import annotations

import flet as ft

from app.core.errors import ApplicationError
from app.ui.viewmodels.quote_details_vm import QuoteDetailsVM, QuoteItemVM


class QuoteDetailsController:
    def __init__(self, page: ft.Page, vm: QuoteDetailsVM, quote_id: str):
        self.page = page
        self.vm = vm
        self.quote_id = quote_id

        # será setado pela Page
        self._render_fn = None

    def bind_render(self, render_fn):
        """A Page registra uma função para re-renderizar a região dela."""
        self._render_fn = render_fn

    def on_route_enter(self) -> None:
        # agenda o carregamento para depois do build (evita update durante construção)
        self.page.run_task(self._load_async)

    async def _load_async(self):
        self.vm.is_loading = True
        self.vm.error = None
        self._render()

        container = self.page.data["container"]

        try:
            dto = container.get_quote_details.execute(self.quote_id)
        except ApplicationError as e:
            self.vm.is_loading = False
            self.vm.error = str(e)
            self._render()
            return

        self.vm.is_loading = False
        self.vm.quote_id = dto.id
        self.vm.customer_name = dto.customer_name
        self.vm.status = dto.status
        self.vm.materials_included = dto.materials_included
        self.vm.total_sale_cents = dto.total_sale_cents
        self.vm.total_sale_brl = self._fmt_brl(dto.total_sale_cents)

        self.vm.items = []
        for i in dto.items:
            item_vm = QuoteItemVM(
                service_name=i.service_name,
                unit=i.unit,
                quantity=i.quantity,
                unit_price_cents=i.unit_price_cents,
                adjustment_cents=i.adjustment_cents,
                line_total_cents=i.line_total_cents,
            )

            # campos formatados para UI
            item_vm.unit_price_brl = self._fmt_brl(i.unit_price_cents)
            item_vm.adjustment_brl = self._fmt_brl(i.adjustment_cents)
            item_vm.line_total_brl = self._fmt_brl(i.line_total_cents)

            self.vm.items.append(item_vm)


        self._render()

    def _render(self) -> None:
        if self._render_fn:
            self._render_fn()

    def _fmt_brl(self, cents: int) -> str:
        neg = cents < 0
        cents = abs(int(cents))
        inteiro = cents // 100
        frac = cents % 100

        s = str(inteiro)
        parts = []
        while s:
            parts.append(s[-3:])
            s = s[:-3]
        inteiro_fmt = ".".join(reversed(parts))
        out = f"{inteiro_fmt},{frac:02d}"
        return f"-{out}" if neg else out

