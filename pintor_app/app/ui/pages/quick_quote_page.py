from __future__ import annotations

import flet as ft

from app.ui.controllers.quick_quote_controller import QuickQuoteController


def QuickQuotePage(page: ft.Page, router) -> ft.Control:
    controller = QuickQuoteController(page, router)

    customer_tf = ft.TextField(label="Nome do cliente", autofocus=True)
    materials_ck = ft.Checkbox(label="Com material (incluso no preço)", value=False)

    def on_create(_):
        controller.create_quote(customer_tf.value or "", bool(materials_ck.value))

    return ft.Container(
        expand=True,
        padding=20,
        content=ft.Column(
            width=520,
            controls=[
                ft.Text("Orçamento rápido", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Cria um orçamento em rascunho (DRAFT)."),
                ft.Divider(),
                customer_tf,
                materials_ck,
                ft.Row(
                    controls=[
                        ft.ElevatedButton("Criar orçamento", on_click=on_create),
                        ft.TextButton("Voltar", on_click=lambda _: router.go("/")),
                    ]
                ),
            ],
        ),
    )
