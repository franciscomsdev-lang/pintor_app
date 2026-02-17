from __future__ import annotations

import flet as ft

from app.core.state import AppContainer
from app.ui.controllers.settings_controller import SettingsController


class SettingsPage(ft.Container):
    """
    Control que o Router consegue colocar em content_container.
    Page continua 'pura': instancia controller e delega.
    """

    def __init__(self, page: ft.Page) -> None:
        super().__init__(expand=True)
        container: AppContainer = page.data["container"]

        self._controller = SettingsController(page=page, container=container)
        self._controller.attach_host(self)   # controller vai renderizar aqui

        # entra na rota e inicia carregamento
        self._controller.on_route_enter()
        self._controller.bind_render()
