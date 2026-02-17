import flet as ft


class AppShell:
    """
    Layout responsivo:
    - Desktop: NavigationRail lateral
    - Mobile: Drawer + AppBar
    - Conteúdo controlado pelo Router
    """

    BREAKPOINT = 900  # largura para trocar mobile/desktop

    def __init__(self, page: ft.Page, router):
        self.page = page
        self.router = router
        self.pagelet_mobile = None

        self.content_container = ft.Container(expand=True)

        # navegação mobile
        self.drawer = ft.NavigationDrawer(
            selected_index=self._selected_index(),
            on_change=self._on_drawer_change,  # async handler abaixo
            controls=[
                ft.Container(height=12),
                ft.NavigationDrawerDestination(icon=ft.Icons.HOME, label="Home"),
                ft.NavigationDrawerDestination(icon=ft.Icons.ADD_BOX, label="Novo orçamento"),
                ft.NavigationDrawerDestination(icon=ft.Icons.SETTINGS, label="Configurações"),
            ],
        )



    # ---------- montagem ----------

    def mount(self):
        self.router.set_container(self.content_container)

        # ouvir resize para responsividade
        self.page.on_resize = lambda _: self._render()

        self._render()

    # ---------- render principal ----------

    def _render(self):
        self.page.controls.clear()

        if self._is_desktop():
            self.page.add(ft.Container(expand=True, content=self._build_desktop_layout()))

        else:
            self.page.add(ft.Container(expand=True, content=self._build_mobile_layout()))


        self.page.update()

    # ---------- layouts ----------

    def _build_desktop_layout(self):
        rail = ft.NavigationRail(
            selected_index=self._selected_index(),
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=self._nav_destinations(),
            on_change=lambda e: self._navigate_by_index(e.control.selected_index),
        )

        return ft.Row(
            expand=True,
            controls=[
                rail,
                ft.VerticalDivider(width=1),
                ft.Column(
                    expand=True,
                    spacing=0,
                    controls=[
                        self._build_appbar(show_menu=False),
                        self.content_container,
                    ],
                ),
            ],
        )

    def _build_mobile_layout(self):
        # Drawer no scaffold (Pagelet)
        self.page.drawer = self.drawer


        self.pagelet_mobile = ft.Pagelet(
            appbar=self._build_appbar(show_menu=True),
            drawer=self.drawer,
            content=self.content_container,
        )
        return self.pagelet_mobile


    # ---------- AppBar ----------

    def _build_appbar(self, show_menu: bool) -> ft.AppBar:
        leading = None
        if show_menu:
            leading = ft.IconButton(
                icon=ft.Icons.MENU,
                on_click=lambda _: self.page.run_task(self._show_drawer),
            )

        return ft.AppBar(
            title=ft.Text("Pintor App"),
            center_title=False,
            bgcolor=ft.Colors.BLUE,
            leading=leading,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.LOGIN,
                    on_click=lambda _: self.router.go("/login"),
                )
            ],
        )

    # ---------- navegação ----------

    def _nav_destinations(self, drawer: bool = False):
        items = [
            (ft.Icons.HOME, "Home", "/"),
            (ft.Icons.ADD_BOX, "Novo orçamento", "/quick-quote"),
            (ft.Icons.SETTINGS, "Configurações", "/settings"),
        ]

        if drawer:
            return [
                ft.ListTile(
                    leading=ft.Icon(icon),
                    title=ft.Text(label),
                    on_click=lambda _, r=route: self._navigate_drawer(r),
                )
                for icon, label, route in items
            ]

        return [
            ft.NavigationRailDestination(
                icon=ft.Icon(icon),
                label=label,
            )
            for icon, label, _ in items
        ]

    def _navigate_by_index(self, index: int, close_drawer: bool = False):
        routes = ["/", "/quick-quote", "/settings"]

        if close_drawer and self.pagelet_mobile and self.pagelet_mobile.drawer:
            self.pagelet_mobile.drawer.open = False
            self.page.update()

        self.router.go(routes[index])



    def _navigate_drawer(self, route: str):
        self.drawer.open = False
        self.page.update()
        self.router.go(route)

    def _open_drawer(self):
        if self.pagelet_mobile and self.pagelet_mobile.drawer:
            self.pagelet_mobile.drawer.open = True
            self.page.update()



    # ---------- helpers ----------

    def _is_desktop(self) -> bool:
        return self.page.width >= self.BREAKPOINT

    def _selected_index(self) -> int:
        path = self.router.current_path or "/"
        routes = ["/", "/quick-quote", "/settings"]
        return routes.index(path) if path in routes else 0
    
    async def _show_drawer(self):
        await self.page.show_drawer()

    async def _on_drawer_change(self, e: ft.Event[ft.NavigationDrawer]):
        routes = ["/", "/quick-quote", "/settings"]
        idx = e.control.selected_index

        await self.page.close_drawer()
        self.router.go(routes[idx])


