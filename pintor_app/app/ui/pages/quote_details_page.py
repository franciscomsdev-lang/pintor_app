from __future__ import annotations

import flet as ft

from app.ui.viewmodels.quote_details_vm import QuoteDetailsVM
from app.ui.controllers.quote_details_controller import QuoteDetailsController


def QuoteDetailsPage(page: ft.Page, router, vm: QuoteDetailsVM, controller: QuoteDetailsController) -> ft.Control:
    body_container = ft.Container()

    def render_body():
        # monta UI a partir do VM (Page pura)
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
                                f"Preço: R$ {it.unit_price_brl} | Ajuste: R$ {it.adjustment_brl} | "
                                f"Total: R$ {it.line_total_brl}"
                            )
                            for it in (vm.items or [])
                        ],
                    ),
                ],
            )

        # update é após build, acionado pelo controller
        page.update()

    # liga o controller ao render
    controller.bind_render(render_body)

    # primeira renderização (loading)
    vm.is_loading = True
    vm.error = None
    render_body()

    # dispara carregamento após build
    controller.on_route_enter()

    return ft.Container(
        expand=True,
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("Detalhes do orçamento", size=20, weight=ft.FontWeight.BOLD),
                body_container,
                ft.Divider(),
                ft.Row(
                    controls=[
                        ft.TextButton(
                            "Adicionar item",
                            on_click=lambda _: router.go(f"/quotes/{vm.quote_id}/edit"),
                        ),

                        ft.TextButton("Novo orçamento rápido", on_click=lambda _: router.go("/quick-quote")),
                        ft.TextButton("Voltar", on_click=lambda _: router.go("/")),
                    ]
                ),
            ]
        ),
    )
