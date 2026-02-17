import flet as ft


def HomePage(page: ft.Page) -> ft.Control:
    router = page.data["router"]

    return ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("🏠 Home — estrutura funcionando!", size=20),
                ft.Text("Teste: criar um orçamento rápido."),
                ft.ElevatedButton(
                    "Novo orçamento rápido",
                    on_click=lambda _: router.go("/quick-quote"),
                ),
                ft.TextButton(
                    "Login",
                    on_click=lambda _: router.go("/login"),
                ),
            ],
        ),
    )
