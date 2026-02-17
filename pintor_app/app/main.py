import flet as ft

from app.core.router import build_router
from app.core.config import load_config
from app.db.database import connect_sqlite
from app.db.migrations import get_migrations, run_migrations
from app.core.state import AppContainer
from app.ui.shell import AppShell


def main(page: ft.Page):
    page.title = "Pintor App"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    # Migrations (startup)
    cfg = load_config()
    conn = connect_sqlite(str(cfg.db_path))
    run_migrations(conn, get_migrations())
    conn.close()

    # Container (DI)
    container = AppContainer.build()

    # Guardar no page para controllers acessarem (sem global solto)
    page.data = {"container": container}

    router = build_router(page)
    page.data["router"] = router
    shell = AppShell(page=page, router=router)

    shell.mount()

    router.go("/")


if __name__ == "__main__":
    ft.run(main)
