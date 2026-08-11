 
import flet as ft

import theme
from models.app_state import get_state
from components.sidebar import sidebar
from components.topbar import topbar
from views.dashboard_view import DashboardView
from views.orders_view import OrdersView
from views.products_view import ProductsView
from views.customers_view import CustomersView
from views.analytics_view import AnalyticsView
from views.settings_view import SettingsView


class MetricFlowApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.estado = get_state()
        self.pestaña_actual = "dashboard"

        self._configurar_pagina()

        self.vistas = {
            "dashboard": DashboardView(self.estado),
            "ordenes": OrdersView(self.estado),
            "productos": ProductsView(self.estado),
            "clientes": CustomersView(self.estado),
            "analitica": AnalyticsView(self.estado),
            "ajustes": SettingsView(self.estado, self.mostrar_snack),
        }

        self.contenedor_sidebar = ft.Container()
        self.contenedor_vista = ft.Container(expand=True, bgcolor=theme.BG)

        self.layout = ft.Row(
            controls=[
                self.contenedor_sidebar,
                ft.Column(
                    controls=[topbar(self.estado.fecha_actual), self.contenedor_vista],
                    spacing=0, expand=True,
                ),
            ],
            spacing=0,
            expand=True,
        )

        self.page.add(self.layout)
        self._mostrar_vista("dashboard")

    def _configurar_pagina(self):
        p = self.page
        p.title = "Metric Flow"
        p.bgcolor = theme.BG
        p.padding = 0
        p.spacing = 0
        p.theme_mode = ft.ThemeMode.DARK
        p.theme = ft.Theme(color_scheme_seed=theme.PRIMARY, font_family=theme.FONT_FAMILY)
        p.window.width = 1280
        p.window.height = 820
        p.window.min_width = 1000
        p.window.min_height = 640

    def _mostrar_vista(self, clave: str):
        self.pestaña_actual = clave
        vista = self.vistas[clave]
        if hasattr(vista, "refrescar"):
            vista.refrescar()
        self.contenedor_vista.content = vista
        self.contenedor_sidebar.content = sidebar(clave, self._ir_a)

    async def _ir_a(self, e):
        clave = e.control.data
        if clave == self.pestaña_actual:
            return
        self._mostrar_vista(clave)
        self.page.update()

    def mostrar_snack(self, texto: str, color: str = None):
        try:
            self.page.show_dialog(
                ft.SnackBar(
                    content=ft.Text(texto, color=theme.TEXT_PRIMARY, weight=ft.FontWeight.W_600),
                    bgcolor=theme.CARD_BG_ALT,
                    duration=2400,
                )
            )
        except Exception:
            pass


def main(page: ft.Page):
    MetricFlowApp(page)


if __name__ == "__main__":
    ft.run(main)
