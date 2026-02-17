import flet as ft
from typing import Callable, Dict, Optional

from app.ui.pages.home_page import HomePage
from app.ui.pages.login_page import LoginPage
from app.ui.pages.quick_quote_page import QuickQuotePage
from app.ui.pages.quote_details_page import QuoteDetailsPage

from app.ui.viewmodels.quote_details_vm import QuoteDetailsVM
from app.ui.controllers.quote_details_controller import QuoteDetailsController

from app.ui.pages.quote_edit_page import QuoteEditPage
from app.ui.controllers.quote_edit_controller import QuoteEditController

from app.ui.viewmodels.quote_edit_vm import QuoteEditVM
from app.ui.controllers.quote_edit_controller import QuoteEditController

# NOVO

from app.ui.pages.settings_page import SettingsPage


class Router:
    def __init__(self, page: ft.Page, routes: Dict[str, Callable[[], ft.Control]]):
        self.page = page
        self.routes = routes
        self.container: ft.Container | None = None
        self.current_path: str = "/"

    def set_container(self, container: ft.Container):
        self.container = container

    def go(self, path: str):
        self.current_path = path
        view = self._resolve(path)
        if self.container:
            self.container.content = view
            self.page.update()

    def refresh(self):
        self.go(self.current_path)

    def _resolve(self, path: str) -> ft.Control:
        builder = self.routes.get(path)
        if builder:
            return builder()

        edit_id = self._match_quote_edit(path)
        if edit_id:
            vm = QuoteEditVM(items=[])
            controller = QuoteEditController(self.page, vm, edit_id)
            return QuoteEditPage(self.page, self, vm, controller)

        quote_id = self._match_quote_details(path)
        if quote_id:
            vm = QuoteDetailsVM(items=[])
            controller = QuoteDetailsController(self.page, vm, quote_id)
            return QuoteDetailsPage(self.page, self, vm, controller)

        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Text(f"404 — rota não encontrada: {path}"),
        )

    def _match_quote_details(self, path: str) -> Optional[str]:
        parts = [p for p in path.split("/") if p]
        if len(parts) == 2 and parts[0] == "quotes":
            return parts[1]
        return None

    def _match_quote_edit(self, path: str) -> Optional[str]:
        parts = [p for p in path.split("/") if p]
        if len(parts) == 3 and parts[0] == "quotes" and parts[2] == "edit":
            return parts[1]
        return None


def build_router(page: ft.Page) -> Router:
    routes = {
        "/": lambda: HomePage(page),
        "/login": lambda: LoginPage(page),
    }

    router = Router(page, routes)

    routes["/quick-quote"] = lambda: QuickQuotePage(page, router)

    # NOVA ROTA
    routes["/settings"] = lambda: SettingsPage(page)

    return router
