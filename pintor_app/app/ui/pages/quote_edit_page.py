from __future__ import annotations

import flet as ft

from app.ui.viewmodels.quote_edit_vm import QuoteEditVM

from app.ui.controllers.quote_edit_controller import QuoteEditController



def QuoteEditPage(page: ft.Page, router, vm: QuoteEditVM, controller: QuoteEditController) -> ft.Control:
    body_container = ft.Container()

    def render_body():
        if vm.is_loading:
            body_container.content = ft.Text("Carregando...")
        elif vm.error:
            body_container.content = ft.Text(vm.error)
        else:
            body_container.content = ft.Column(
                spacing=8,
                controls=[
                    ft.Text(f"ID: {vm.quote_id}"),
                    ft.Text(f"Cliente: {vm.customer_name}"),
                    ft.Text(f"Status: {vm.status}"),
                    ft.Text(f"Com material: {'Sim' if vm.materials_included else 'Não'}"),
                    ft.Text(f"Total: R$ {vm.total_sale_brl}"),
                    ft.Divider(),
                    ft.Text(f"Itens: {len(vm.items or [])}", weight=ft.FontWeight.BOLD),
                    ft.Column(
                        spacing=6,
                        controls=[
                            ft.Text(
                                f"- {it.service_name} | {it.quantity} {it.unit} | "
                                f"Preço: {it.unit_price_brl} | Ajuste: {it.adjustment_brl} | "
                                f"Total: {it.line_total_brl}"
                            )
                            for it in (vm.items or [])
                        ],
                    ),
                    ft.Divider(),
                    ft.Text("Adicionar item", weight=ft.FontWeight.BOLD),
                    ft.Dropdown(
                        label="Serviço",
                        value=controller.selected_service_id,  # <- controla o que aparece selecionado
                        options=[ft.dropdown.Option(s.id, s.name) for s in controller.services],
                        on_select=lambda e: controller.select_service(e.data),
                    ),
                    ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        width=398,
                        controls=[
                            ft.TextField(
                                label="Unidade (ex: m², dia)",
                                value=vm.new_unit,
                                on_change=lambda e: controller.set_unit(e.control.value),
                                disabled=vm.unit_locked,   # <- trava
                                expand=True,
                            ),
                            ft.OutlinedButton(
                                "Alterar" if vm.unit_locked else "Travar",
                                on_click=lambda e: controller.toggle_unit_lock(),
                            ),
                        ],
                    ),

                    ft.TextField(label="Quantidade", value=vm.new_quantity, on_change=lambda e: controller.set_quantity(e.control.value)),
                    ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        width=398,
                        controls=[
                            ft.TextField(
                                label="Preço unitário (R$)",
                                value=vm.new_unit_price,
                                on_change=lambda e: controller.set_unit_price(e.control.value),
                                disabled=vm.unit_price_locked,  # <- trava
                                expand=True,
                            ),
                            ft.OutlinedButton(
                                "Alterar" if vm.unit_price_locked else "Travar",
                                on_click=lambda e: controller.toggle_unit_price_lock(),
                            ),
                        ],
                    ),

                    ft.TextField(label="Ajuste (R$)", value=vm.new_adjustment, on_change=lambda e: controller.set_adjustment(e.control.value)),
                    ft.Text(vm.form_error or "", color=ft.Colors.RED),
                    ft.ElevatedButton("Adicionar item", on_click=lambda _: controller.add_item(), disabled=vm.is_saving),
                ],
            )

        page.update()

    controller.bind_render(render_body)

    
    render_body()

    controller.on_route_enter()

    return ft.Container(
        expand=True,
        padding=20,
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("Editar orçamento", size=20, weight=ft.FontWeight.BOLD),
                body_container,
                ft.Divider(),
                ft.Row(
                    controls=[
                        ft.TextButton("Voltar detalhes", on_click=lambda _: router.go(f"/quotes/{vm.quote_id}")),
                        ft.TextButton("Home", on_click=lambda _: router.go("/")),
                    ]
                ),
            ]
        ),
    )
