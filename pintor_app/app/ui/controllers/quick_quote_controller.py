from __future__ import annotations

import flet as ft

from app.core.errors import ApplicationError
from app.core.use_cases.create_quick_quote_draft import CreateQuickQuoteDraftInput


class QuickQuoteController:
    def __init__(self, page: ft.Page, router):
        self.page = page
        self.router = router

    def create_quote(self, customer_name: str, materials_included: bool) -> None:
        container = self.page.data["container"]

        try:
            quote_id = container.create_quick_quote_draft.execute(
                CreateQuickQuoteDraftInput(
                    customer_name=customer_name,
                    materials_included=materials_included,
                )
            )
        except ApplicationError as e:
            self.page.snack_bar = ft.SnackBar(ft.Text(str(e)))
            self.page.snack_bar.open = True
            self.page.update()
            return

        # Navega para uma tela simples de "detalhe" (vamos criar agora)
        self.router.go(f"/quotes/{quote_id}/edit")
