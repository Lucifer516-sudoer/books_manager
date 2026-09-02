import flet as ft

from ui.views import settings_view

navigation_bar = ft.NavigationBar(
    destinations=[
        ft.NavigationBarDestination(
            icon=ft.Icons.HOME,
            label="Home",
        ),
        ft.NavigationBarDestination(
            icon=ft.Icons.SETTINGS,
            label="Settings",
        ),
    ]
)

pages = {
    "/home": ft.View(
        controls=[
            ft.SafeArea(content=ft.Text("Home")),
        ],
        navigation_bar=navigation_bar,
    ),
    "/settings": ft.View(
        controls=[
            settings_view.SetingsView(),
        ],
        navigation_bar=navigation_bar,
    ),
}

route_order = list(pages.keys())  # so we can map route -> nav bar index


async def get_to(route: str, view: ft.View, *, page: ft.Page) -> str:
    page.views.clear()
    page.views.append(view)

    if page.navigation_bar is not None:
        page.navigation_bar.selected_index = route_order.index(route)

    return page.route


async def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.navigation_bar = navigation_bar

    async def _on_route_change(e: ft.RouteChangeEvent):
        route = page.route
        if route in pages:
            await get_to(route, pages[route], page=page)
            page.update()

    page.on_route_change = _on_route_change

    async def _on_nav_change(e: ft.ControlEvent):
        index = navigation_bar.selected_index
        await page.push_route(route_order[index])

    navigation_bar.on_change = _on_nav_change  # type: ignore

    await page.push_route("/home")


if __name__ == "__main__":
    ft.run(main)  # type: ignore
