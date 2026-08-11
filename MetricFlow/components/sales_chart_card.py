"""
components/sales_chart_card.py — Tarjeta "Rendimiento de Ventas Mensual":
gráfico de líneas (Ventas vs Meta) con leyenda y punto destacado.
"""
import flet as ft
import flet_charts as fch
import theme


def _leyenda() -> ft.Row:
    def item(color, texto):
        return ft.Row(
            controls=[
                ft.Container(width=14, height=2.5, bgcolor=color, border_radius=2),
                ft.Text(texto, size=11.5, color=theme.TEXT_SECONDARY),
            ],
            spacing=6, tight=True,
        )

    return ft.Row(controls=[item(theme.PRIMARY, "Ventas"), item(theme.ACCENT_BLUE, "Meta")], spacing=16)


def sales_chart_card(meses: list, serie_ventas: list, serie_meta: list) -> ft.Container:
    max_y = max(max(serie_ventas), max(serie_meta)) * 1.25

    linea_ventas = fch.LineChartData(
        points=[fch.LineChartDataPoint(x=i, y=v) for i, v in enumerate(serie_ventas)],
        curved=True, curve_smoothness=0.35,
        color=theme.PRIMARY, stroke_width=3, rounded_stroke_cap=True,
        below_line_bgcolor=ft.Colors.with_opacity(0.10, theme.PRIMARY),
    )
    linea_meta = fch.LineChartData(
        points=[fch.LineChartDataPoint(x=i, y=v) for i, v in enumerate(serie_meta)],
        curved=True, curve_smoothness=0.35,
        color=theme.ACCENT_BLUE, stroke_width=2.5, dash_pattern=[7, 5],
    )

    grafico = fch.LineChart(
        data_series=[linea_ventas, linea_meta],
        min_y=0, max_y=max_y,
        interactive=True,
        border=ft.Border.all(0, "transparent"),
        horizontal_grid_lines=fch.ChartGridLines(interval=max_y / 4, color=theme.BORDER, width=1),
        vertical_grid_lines=fch.ChartGridLines(interval=1000, color="transparent", width=0),
        left_axis=fch.ChartAxis(
            show_labels=True, label_size=40,
            labels=[fch.ChartAxisLabel(value=v, label=str(int(v))) for v in
                    [0, max_y / 4, max_y / 2, max_y * 3 / 4, max_y]],
        ),
        bottom_axis=fch.ChartAxis(
            show_labels=True,
            labels=[fch.ChartAxisLabel(value=i, label=m) for i, m in enumerate(meses)],
        ),
        top_axis=fch.ChartAxis(show_labels=False),
        right_axis=fch.ChartAxis(show_labels=False),
        animation=ft.Animation(500),
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Rendimiento de Ventas Mensual", size=15.5, weight=ft.FontWeight.W_700,
                                 color=theme.TEXT_PRIMARY),
                        _leyenda(),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(content=grafico, height=260, padding=ft.Padding.only(top=10)),
            ],
            spacing=16,
        ),
        bgcolor=theme.CARD_BG,
        border=ft.Border.all(1, theme.BORDER),
        border_radius=theme.CARD_RADIUS,
        padding=20,
        expand=True,
    )