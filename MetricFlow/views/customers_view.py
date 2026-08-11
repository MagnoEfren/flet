"""
views/customers_view.py — Pantalla "Clientes": tabla de clientes.
"""
import flet as ft
import theme
from components.section_card import section_card


class CustomersView(ft.Container):
    def __init__(self, estado):
        super().__init__()
        self.estado = estado
        self.expand = True
        self.padding = ft.Padding.only(left=28, right=28, top=14, bottom=28)

    def refrescar(self):
        e = self.estado

        encabezado = ft.Text("Clientes", size=22, weight=ft.FontWeight.W_800, color=theme.TEXT_PRIMARY)

        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("CLIENTE", size=11.5, color=theme.TEXT_MUTED)),
                ft.DataColumn(label=ft.Text("CORREO", size=11.5, color=theme.TEXT_MUTED)),
                ft.DataColumn(label=ft.Text("PAÍS", size=11.5, color=theme.TEXT_MUTED)),
                ft.DataColumn(label=ft.Text("PEDIDOS", size=11.5, color=theme.TEXT_MUTED), numeric=True),
                ft.DataColumn(label=ft.Text("GASTADO", size=11.5, color=theme.TEXT_MUTED), numeric=True),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(c["nombre"], size=12.5, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY)),
                        ft.DataCell(ft.Text(c["correo"], size=12.5, color=theme.TEXT_SECONDARY)),
                        ft.DataCell(ft.Text(c["pais"], size=12.5, color=theme.TEXT_SECONDARY)),
                        ft.DataCell(ft.Text(str(c["pedidos"]), size=12.5, color=theme.TEXT_SECONDARY)),
                        ft.DataCell(ft.Text(c["gastado"], size=12.5, weight=ft.FontWeight.W_700, color=theme.PRIMARY)),
                    ]
                )
                for c in e.clientes
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
                section_card(ft.Column(controls=[tabla], scroll=ft.ScrollMode.AUTO), expand=True),
            ],
            spacing=18,
            expand=True,
        )
