import flet as ft


def LoginPage(page: ft.Page) -> ft.Control:
    return ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER,
        content=ft.Text("🔐 Login Page", size=20),
    )
