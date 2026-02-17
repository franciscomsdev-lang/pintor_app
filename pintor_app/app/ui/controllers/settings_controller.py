from __future__ import annotations

import re
from typing import Optional

import flet as ft

from app.core.state import AppContainer
from app.core.use_cases.list_services import ListServicesRequest
from app.core.use_cases.create_service import CreateServiceRequest
from app.core.use_cases.delete_service import DeleteServiceRequest

from app.ui.viewmodels.settings_vm import SettingsVM


class SettingsController:
    def __init__(self, page: ft.Page, container: AppContainer) -> None:
        self.page = page
        self.container = container
        self.vm = SettingsVM()
        self._host: ft.Container | None = None
        self._pending_delete_id: str | None = None



        # refs
        self._dialog: Optional[ft.AlertDialog] = None

    # =========================
    # Router hooks
    # =========================
    def on_route_enter(self) -> None:
        self.page.run_task(self._load_services)  # sem ()



    # =========================
    # Render / binding
    # =========================
    def bind_render(self) -> None:
        if not self._host:
            return
        self._host.content = self.render_view()
        self.page.update()  # permitido aqui (bind_render)


    def render_view(self) -> ft.Control:
        selected = self.vm.selected_service()

        header = ft.Row(
            controls=[
                ft.Text("Configurações • Serviços",size=20, weight=ft.FontWeight.W_600),
                ft.Container(expand=True),
                ft.ElevatedButton("Novo serviço", icon=ft.Icons.ADD, on_click=lambda e: self.open_new_service_dialog()),
                ft.OutlinedButton(
                    "Excluir selecionado",
                    icon=ft.Icons.DELETE_OUTLINE,
                    on_click=lambda e: self.delete_selected_service(),
                    disabled=(self.vm.selected_service_id is None),
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        status_line = ft.Row(
            controls=[
                ft.ProgressRing(visible=self.vm.loading),
                ft.Text(self.vm.error or "", color=ft.Colors.RED, visible=bool(self.vm.error)),
            ],
            spacing=12,
        )

        services_dropdown = ft.Dropdown(
            label="Serviço",
            value=self.vm.selected_service_id,
            options=[
                ft.dropdown.Option(
                    s.id,
                    f"{s.name} • {s.unit} • R$ {self._cents_to_br(s.default_unit_price_cents)}",
                )
                for s in self.vm.services
            ],
            on_select=self._on_select_service,   # (sua versão)
        )

        selected_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Selecionado", size=20, weight=ft.FontWeight.W_600),
                    ft.Text(
                        f"{selected.name} • {selected.unit} • R$ {self._cents_to_br(selected.default_unit_price_cents)}"
                        if selected else "Nenhum serviço selecionado"
                    ),
                ],
                spacing=6,
            ),
            padding=12,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=10,
        )

        items: list[ft.Control] = []
        for s in self.vm.services:
            items.append(
                ft.ListTile(
                    title=ft.Text(s.name),
                    subtitle=ft.Text(f"Unidade: {s.unit} • Preço padrão: R$ {self._cents_to_br(s.default_unit_price_cents)}"),
                    selected=(self.vm.selected_service_id == s.id),
                    on_click=lambda e, sid=s.id: self._select_service_id(sid),
                )
            )
            items.append(ft.Divider(height=1))

        list_view = ft.ListView(
            controls=items if items else [ft.Text("Nenhum serviço cadastrado ainda.")],
            spacing=0,
            expand=True,  # CHAVE
        )

        
        list_panel = ft.Container(
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Text("Catálogo"),
                    ft.Container(expand=True, content=list_view),
                ],
            ),
        )



        # Top-level control (não View!)
        
        return ft.Container(
            expand=True,
            padding=16,
            alignment=ft.Alignment.TOP_LEFT,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Text("Settings OK"),
                    header,
                    status_line,
                    services_dropdown,
                    selected_card,
                    list_panel
                ],
            ),
        )



    # =========================
    # Actions
    # =========================
    async def _load_services(self) -> None:
        self.vm.loading = True
        self.vm.error = None
        self.bind_render()

        try:
            resp = await self.container.list_services.execute(ListServicesRequest())
            self.vm.services = list(resp.services)

            # manter seleção se ainda existir, senão selecionar o primeiro
            if self.vm.selected_service_id and any(s.id == self.vm.selected_service_id for s in self.vm.services):
                pass
            else:
                self.vm.selected_service_id = self.vm.services[0].id if self.vm.services else None

        except Exception as ex:
            self.vm.error = str(ex)
        finally:
            self.vm.loading = False
            self.bind_render()

    def _select_service_id(self, service_id: str) -> None:
        self.vm.selected_service_id = service_id
        self.bind_render()

    def _on_select_service(self, e: ft.ControlEvent) -> None:
        value = getattr(e.control, "value", None) or getattr(e, "data", None)
        if value:
            self.vm.selected_service_id = value
            self.bind_render()


    def open_new_service_dialog(self) -> None:
        self.vm.dialog_open = True
        self.vm.error = None

        name_tf = ft.TextField(
            label="Nome do serviço",
            value=self.vm.new_name,
            autofocus=True,
            on_change=lambda e: self._set_new_name(e.control.value),
        )

        unit_dd = ft.Dropdown(
            label="Unidade",
            value=self.vm.new_unit,
            options=[
                ft.dropdown.Option("M2", "M²"),
                ft.dropdown.Option("DAY", "Diária"),
                ft.dropdown.Option("ROOM", "Cômodo"),
                ft.dropdown.Option("UNIT", "Unidade"),
            ],
            on_select=lambda e: self._set_new_unit(e.control.value),
        )

        price_tf = ft.TextField(
            label="Preço padrão (R$)",
            hint_text="Ex: 120,00",
            value=self.vm.new_price_text,
            on_change=lambda e: self._set_new_price_text(e.control.value),
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        self._dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Novo serviço"),
            content=ft.Column(
                tight=True,
                controls=[
                    name_tf,
                    unit_dd,
                    price_tf,
                    ft.Text(self.vm.error or "", color=ft.Colors.RED, visible=bool(self.vm.error)),
                ],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.close_dialog()),
                ft.ElevatedButton("Salvar", icon=ft.Icons.CHECK, on_click=lambda e: self.create_service()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # ✅ JEITO MAIS COMPATÍVEL:
        if self._dialog not in self.page.overlay:
            self.page.overlay.append(self._dialog)

        self._dialog.open = True
        self.page.update()


    def close_dialog(self) -> None:
        if self._dialog:
            self._dialog.open = False
            self.page.update()
        self.vm.dialog_open = False


    def _set_new_name(self, v: str) -> None:
        self.vm.new_name = v

    def _set_new_unit(self, v: str) -> None:
        self.vm.new_unit = v

    def _set_new_price_text(self, v: str) -> None:
        self.vm.new_price_text = v

    def create_service(self) -> None:
        self.page.run_task(self._create_service_async)  # sem ()


    async def _create_service_async(self) -> None:
        self.vm.loading = True
        self.vm.error = None
        self.bind_render()

        try:
            cents = self._br_to_cents(self.vm.new_price_text)

            await self.container.create_service.execute(
                CreateServiceRequest(
                    name=self.vm.new_name,
                    unit=self.vm.new_unit,
                    default_unit_price_cents=cents,
                )
            )

            # reset form
            self.vm.new_name = ""
            self.vm.new_unit = "M2"
            self.vm.new_price_text = ""

            # fechar dialog e recarregar
            self.close_dialog()
            await self._load_services()

        except Exception as ex:
            self.vm.error = str(ex)
            # atualizar dialog (erro aparece lá)
            if self._dialog:
                self._dialog.content.controls[-1].value = self.vm.error or ""
                self._dialog.content.controls[-1].visible = bool(self.vm.error)
                self.page.update()
        finally:
            self.vm.loading = False
            self.bind_render()

    def delete_selected_service(self) -> None:
        service_id = self.vm.selected_service_id
        if not service_id:
            return

        self._pending_delete_id = service_id
        self.page.run_task(self._delete_selected_pending)




    async def _delete_selected_async(self, service_id: str) -> None:
        self.vm.loading = True
        self.vm.error = None
        self.bind_render()

        try:
            await self.container.delete_service.execute(DeleteServiceRequest(service_id=service_id))
            # após excluir, recarrega e ajusta seleção
            await self._load_services()
        except Exception as ex:
            self.vm.error = str(ex)
        finally:
            self.vm.loading = False
            self.bind_render()

    async def _delete_selected_pending(self) -> None:
        service_id = self._pending_delete_id
        self._pending_delete_id = None
        if not service_id:
            return
        await self._delete_selected_async(service_id)

    # =========================
    # Helpers (money)
    # =========================
    def _br_to_cents(self, txt: str) -> int:
        """
        Converte "120,50" ou "120.50" para cents (12050).
        Aceita vazio -> 0.
        """
        s = (txt or "").strip()
        if not s:
            return 0

        # mantém dígitos e separadores
        s = re.sub(r"[^\d,\.]", "", s)

        # se tiver vírgula, assume vírgula decimal (pt-BR)
        if "," in s:
            s = s.replace(".", "")
            s = s.replace(",", ".")
        # agora s é formato decimal com ponto
        if s.count(".") > 1:
            raise ValueError("Preço inválido.")

        if "." in s:
            whole, frac = s.split(".", 1)
            frac = (frac + "00")[:2]
        else:
            whole, frac = s, "00"

        if whole == "":
            whole = "0"

        cents = int(whole) * 100 + int(frac)
        return cents

    def _cents_to_br(self, cents: int) -> str:
        cents = int(cents or 0)
        whole = cents // 100
        frac = cents % 100
        return f"{whole:,}".replace(",", ".") + f",{frac:02d}"

    def attach_host(self, host: ft.Container) -> None:
        self._host = host
