"""
views/orders_view.py — Pantalla "Órdenes": tabla de pedidos con estado.
"""
import flet as ft
import theme
from components.section_card import section_card
from components.status_badge import status_badge
from services import data_service as ds


class OrdersView(ft.Container):
    def __init__(self, estado):
        super().__init__()
        self.estado = estado
        self.expand = True
        self.padding = ft.Padding.only(left=28, right=28, top=14, bottom=28)

    def refrescar(self):
        e = self.estado

        encabezado = ft.Text("Órdenes", size=22, weight=ft.FontWeight.W_800, color=theme.TEXT_PRIMARY)

        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("ID", size=11.5, color=theme.TEXT_MUTED)),
                ft.DataColumn(label=ft.Text("CLIENTE", size=11.5, color=theme.TEXT_MUTED)),
                ft.DataColumn(label=ft.Text("PRODUCTO", size=11.5, color=theme.TEXT_MUTED)),
                ft.DataColumn(label=ft.Text("FECHA", size=11.5, color=theme.TEXT_MUTED)),
                ft.DataColumn(label=ft.Text("ESTADO", size=11.5, color=theme.TEXT_MUTED)),
                ft.DataColumn(label=ft.Text("TOTAL", size=11.5, color=theme.TEXT_MUTED), numeric=True),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(o["id"], size=12.5, color=theme.TEXT_SECONDARY)),
                        ft.DataCell(ft.Text(o["cliente"], size=12.5, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY)),
                        ft.DataCell(ft.Text(o["producto"], size=12.5, color=theme.TEXT_SECONDARY)),
                        ft.DataCell(ft.Text(o["fecha"], size=12.5, color=theme.TEXT_SECONDARY)),
                        ft.DataCell(status_badge(o["estado"], ds.color_por_estado_orden(o["estado"]))),
                        ft.DataCell(ft.Text(o["total"], size=12.5, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY)),
                    ]
                )
                for o in e.ordenes
            ],
            heading_row_color=theme.CARD_BG_ALT,
            heading_row_height=42,
            data_row_min_height=52,
            divider_thickness=0.6,
            horizontal_lines=ft.BorderSide(0.6, theme.BORDER),
            column_spacing=28,
        )

        self.content = ft.Column(
            controls=[
                encabezado,
                section_card(
                    ft.Column(controls=[tabla], scroll=ft.ScrollMode.AUTO),
                    expand=True,
                ),
            ],
            spacing=18,
            expand=True,
        )
