from __future__ import annotations

import flet as ft
from decimal import Decimal, InvalidOperation

from app.core.errors import ApplicationError
from app.core.use_cases.add_item_to_quote import AddItemToQuoteInput
from app.ui.viewmodels.quote_edit_vm import QuoteEditVM, QuoteEditItemVM
from app.core.use_cases.list_services import ListServicesRequest



class QuoteEditController:
    def __init__(self, page: ft.Page, vm: QuoteEditVM, quote_id: str):
        self.page = page
        self.vm = vm
        self.quote_id = quote_id
        self._render_fn = None
        self.services = []
        self.selected_service_id: str | None = None


    def bind_render(self, render_fn):
        self._render_fn = render_fn

    def _render(self):
        if self._render_fn:
            self._render_fn()

    def on_route_enter(self) -> None:
        self.page.run_task(self._load_async)


    async def _load_async(self):
        self.vm.is_loading = True
        self.vm.error = None
        self.selected_service_id = None

        self._render()

        container = self.page.data["container"]

        try:
            # 1) Quote details (no seu projeto isso é SYNC)
            dto = container.get_quote_details.execute(self.quote_id)

            # 2) Services catalog (use case é ASYNC)
            services_resp = await container.list_services.execute(ListServicesRequest())
            self.services = list(services_resp.services)

        except ApplicationError as e:
            self.vm.is_loading = False
            self.vm.error = str(e)
            self._render()
            return
        except Exception as e:
            # cobre ValueError do repo / etc
            self.vm.is_loading = False
            self.vm.error = str(e)
            self._render()
            return

        # preencher VM com dados do quote
        self.vm.is_loading = False
        self.vm.quote_id = dto.id
        self.vm.customer_name = dto.customer_name
        self.vm.status = dto.status
        self.vm.materials_included = dto.materials_included
        self.vm.total_sale_cents = dto.total_sale_cents
        self.vm.total_sale_brl = self._fmt_brl(dto.total_sale_cents)

        self.vm.items = []
        for i in dto.items:
            item_vm = QuoteEditItemVM(
                item_id=i.id,
                service_name=i.service_name,
                unit=i.unit,
                quantity=i.quantity,
                unit_price_cents=i.unit_price_cents,
                adjustment_cents=i.adjustment_cents,
                line_total_cents=i.line_total_cents,
            )
            item_vm.unit_price_brl = self._fmt_brl(i.unit_price_cents)
            item_vm.adjustment_brl = self._fmt_brl(i.adjustment_cents)
            item_vm.line_total_brl = self._fmt_brl(i.line_total_cents)
            self.vm.items.append(item_vm)

        self._render()


    def select_service(self, service_id: str) -> None:
        self.selected_service_id = service_id

        svc = next((s for s in self.services if s.id == service_id), None)
        if svc is None:
            self.vm.form_error = "Serviço selecionado não encontrado."
            self._render()
            return

        # autopreenche
        self.vm.new_service_name = svc.name
        self.vm.new_unit = svc.unit
        self.vm.new_unit_price = self._fmt_brl(svc.default_unit_price_cents)

        # trava por padrão
        self.vm.unit_locked = True
        self.vm.unit_price_locked = True

        self.vm.form_error = None
        self._render()

    # setters do form (UI -> Controller)
    def set_service_name(self, v: str) -> None:
        self.vm.new_service_name = v
        self.vm.form_error = None
        

    def set_unit(self, v: str) -> None:
        self.vm.new_unit = v
        self.vm.form_error = None

    def toggle_unit_lock(self) -> None:
        self.vm.unit_locked = not self.vm.unit_locked
        self._render()

        

    def set_quantity(self, v: str) -> None:
        self.vm.new_quantity = v
        self.vm.form_error = None
        

    def set_unit_price(self, v: str) -> None:
        self.vm.new_unit_price = v
        self.vm.form_error = None

    def toggle_unit_price_lock(self) -> None:
        self.vm.unit_price_locked = not self.vm.unit_price_locked
        self._render()

        

    def set_adjustment(self, v: str) -> None:
        self.vm.new_adjustment = v
        self.vm.form_error = None
        

    def add_item(self) -> None:
        name = (self.vm.new_service_name or "").strip()
        if not name:
            self.vm.form_error = "Serviço é obrigatório."
            self._render()
            return

        unit = (self.vm.new_unit or "").strip()
        if not unit:
            self.vm.form_error = "Unidade é obrigatória."
            self._render()
            return

        qty: int | None = None

        if unit == "M2":
            qty_dec = self._parse_qty_decimal_br(self.vm.new_quantity)
            if qty_dec is None or qty_dec <= 0:
                self.vm.form_error = "Quantidade inválida para m² (ex: 12,5)."
                self._render()
                return

            # COMPAT: enquanto o core não aceita Decimal, arredonda para int
            # (você pode trocar para truncar se preferir)
            qty = int(qty_dec.to_integral_value(rounding="ROUND_HALF_UP"))

        else:
            qty = self._parse_int(self.vm.new_quantity)
            if qty is None or qty <= 0:
                self.vm.form_error = "Quantidade inválida."
                self._render()
                return


        unit_price_cents = self._parse_brl_to_cents(self.vm.new_unit_price, allow_empty=False)
        if unit_price_cents is None or unit_price_cents < 0:
            self.vm.form_error = "Preço unitário inválido."
            self._render()
            return

        adjustment_cents = self._parse_brl_to_cents(self.vm.new_adjustment, allow_empty=True)
        if adjustment_cents is None:
            self.vm.form_error = "Ajuste inválido."
            self._render()
            return

        async def _job():
            await self._add_item_async(name, unit, qty, unit_price_cents, adjustment_cents)

        self.page.run_task(_job)


    async def _add_item_async(self, name: str, unit: str, qty: int, unit_price_cents: int, adjustment_cents: int):
        container = self.page.data["container"]

        self.vm.is_saving = True
        self.vm.form_error = None
        self._render()

        try:
            container.add_item_to_quote.execute(
                AddItemToQuoteInput(
                    quote_id=self.quote_id,
                    service_name=name,
                    unit=unit,
                    quantity=qty,
                    unit_price_cents=unit_price_cents,
                    adjustment_cents=adjustment_cents,
                    description_client="",
                )
            )
        except ApplicationError as e:
            self.vm.is_saving = False
            self.vm.form_error = str(e)
            self._render()
            return

        await self._load_async()

        self.vm.new_service_name = ""
        self.vm.new_unit = ""
        self.vm.new_quantity = ""
        self.vm.new_unit_price = ""
        self.vm.new_adjustment = "0"
        self.vm.is_saving = False
        self.selected_service_id = None
        self.vm.unit_locked = True
        self.vm.unit_price_locked = True

        self._render()

    def _parse_int(self, raw: str):
        try:
            s = (raw or "").strip()
            if not s:
                return None
            return int(s)
        except ValueError:
            return None

    def _parse_brl_to_cents(self, raw: str, allow_empty: bool):
        s = (raw or "").strip()
        if s == "":
            return 0 if allow_empty else None
        try:
            s = s.replace("R$", "").strip()
            s = s.replace(".", "").replace(",", ".")
            value = Decimal(s)
            return int((value * 100).quantize(Decimal("1")))
        except (InvalidOperation, ValueError):
            return None

    def _parse_qty_decimal_br(self, raw: str) -> Decimal | None:
        s = (raw or "").strip()
        if not s:
            return None
        # pt-BR: 12,5
        s = s.replace(".", "").replace(",", ".")
        try:
            q = Decimal(s)
        except (InvalidOperation, ValueError):
            return None
        return q


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
