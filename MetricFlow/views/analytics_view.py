"""
views/analytics_view.py — Pantalla "Analítica": métricas resumen y
ventas por categoría (gráfico de barras).
"""
import flet as ft
import flet_charts as fch
import theme
from components.metric_card import metric_card
from components.section_card import section_card, section_header


class AnalyticsView(ft.Container):
    def __init__(self, estado):
        super().__init__()
        self.estado = estado
        self.expand = True
        self.padding = ft.Padding.only(left=28, right=28, top=14, bottom=28)

    def refrescar(self):
        e = self.estado

        encabezado = ft.Text("Analítica", size=22, weight=ft.FontWeight.W_800, color=theme.TEXT_PRIMARY)

        fila_resumen = ft.Row(
            controls=[
                metric_card(m["titulo"], m["valor"], m["delta"], m["positivo"])
                for m in e.resumen_analitica
            ],
            spacing=16,
        )

        max_valor = max(c["valor"] for c in e.ventas_por_categoria) * 1.2
        grupos = [
            fch.BarChartGroup(
                x=i,
                rods=[
                    fch.BarChartRod(
                        from_y=0, to_y=c["valor"], color=theme.PRIMARY,
                        width=34, border_radius=8,
                        bgcolor=theme.CARD_BG_ALT, bg_from_y=0, bg_to_y=max_valor,
                    )
                ],
            )
            for i, c in enumerate(e.ventas_por_categoria)
        ]

        grafico = fch.BarChart(
            groups=grupos,
            min_y=0, max_y=max_valor,
            interactive=True,
            border=ft.Border.all(0, "transparent"),
            horizontal_grid_lines=fch.ChartGridLines(interval=max_valor / 4, color=theme.BORDER, width=1),
            left_axis=fch.ChartAxis(show_labels=True, label_size=44),
            bottom_axis=fch.ChartAxis(
                show_labels=True,
                labels=[fch.ChartAxisLabel(value=i, label=c["categoria"])
                        for i, c in enumerate(e.ventas_por_categoria)],
            ),
            top_axis=fch.ChartAxis(show_labels=False),
            right_axis=fch.ChartAxis(show_labels=False),
            animation=ft.Animation(500),
        )

        tarjeta_grafico = section_card(
            ft.Column(
                controls=[
                    section_header("Ventas por Categoría"),
                    ft.Container(content=grafico, height=280, padding=ft.Padding.only(top=10)),
                ],
                spacing=16,
            ),
            expand=True,
        )

        self.content = ft.Column(
            controls=[encabezado, fila_resumen, tarjeta_grafico],
            spacing=18,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
