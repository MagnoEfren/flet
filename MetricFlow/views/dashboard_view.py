"""
views/dashboard_view.py — Pantalla principal del dashboard.
"""
import flet as ft
import theme
from components.metric_card import metric_card
from components.section_card import section_card, section_header
from components.heatmap_card import heatmap_card
from components.sales_chart_card import sales_chart_card
from components.country_tile import country_tile
from components.growth_indicator import growth_indicator


class DashboardView(ft.Container):
    def __init__(self, estado):
        super().__init__()
        self.estado = estado
        self.expand = True
        self.padding = ft.Padding.only(left=28, right=28, top=14, bottom=28)

    def refrescar(self):
        e = self.estado

        fila_metricas = ft.Row(
            controls=[
                metric_card(m["titulo"], m["valor"], m["delta"], m["positivo"], self.estado.rango_fechas)
                for m in e.metricas
            ],
            spacing=16,
        )

        self.content = ft.Column(
            controls=[
                fila_metricas,
                ft.Row(
                    controls=[
                        heatmap_card(e.horas_heatmap, e.dias_heatmap, e.matriz_heatmap),
                        sales_chart_card(e.meses_ventas, e.serie_ventas, e.serie_meta),
                    ],
                    spacing=16,
                ),
                ft.Row(
                    controls=[
                        section_card(
                            ft.Column(
                                controls=[
                                    section_header("Ventas por País", "Ver Todo"),
                                    ft.Row(
                                        controls=[
                                            country_tile(p["bandera"], p["pais"], p["productos"])
                                            for p in e.ventas_pais[:3]
                                        ],
                                        spacing=12,
                                    ),
                                    ft.Row(
                                        controls=[
                                            country_tile(p["bandera"], p["pais"], p["productos"])
                                            for p in e.ventas_pais[3:]
                                        ],
                                        spacing=12,
                                    ),
                                ],
                                spacing=16,
                            ),
                            expand=True,
                        ),
                        section_card(self._tabla_top_productos(e.top_productos), expand=True),
                    ],
                    spacing=16,
                ),
            ],
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _tabla_top_productos(self, productos: list) -> ft.Column:
        encabezado = section_header("Top Productos", "Ver Todo")

        fila_titulos = ft.Row(
            controls=[
                ft.Container(content=ft.Text("PRODUCTO", size=10.5, color=theme.TEXT_MUTED), expand=3),
                ft.Container(content=ft.Text("INGRESOS", size=10.5, color=theme.TEXT_MUTED), expand=2),
                ft.Container(content=ft.Text("VENTAS", size=10.5, color=theme.TEXT_MUTED), expand=2),
                ft.Container(content=ft.Text("CREC.", size=10.5, color=theme.TEXT_MUTED), expand=2),
            ],
        )

        filas = [fila_titulos, ft.Divider(color=theme.BORDER, height=1)]
        for p in productos:
            filas.append(
                ft.Row(
                    controls=[
                        ft.Container(content=ft.Text(p["producto"], size=12.5, weight=ft.FontWeight.W_600,
                                                       color=theme.TEXT_PRIMARY), expand=3),
                        ft.Container(content=ft.Text(p["ingresos"], size=12.5, color=theme.TEXT_SECONDARY), expand=2),
                        ft.Container(content=ft.Text(str(p["ventas"]), size=12.5, color=theme.TEXT_SECONDARY), expand=2),
                        ft.Container(content=growth_indicator(p["crecimiento"]), expand=2),
                    ],
                )
            )
            filas.append(ft.Divider(color=theme.BORDER, height=1))

        return ft.Column(controls=[encabezado, ft.Column(controls=filas, spacing=12)], spacing=16)