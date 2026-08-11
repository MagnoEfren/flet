"""
components/heatmap_card.py — Tarjeta "Pedidos por Hora": mapa de calor
con intensidad de verde según volumen de pedidos por día/hora.
"""
import flet as ft
import theme
from services import data_service as ds

_TAMAÑO_CELDA = 30


def _leyenda() -> ft.Row:
    niveles = [("200>", 1), ("500>", 2), ("1,000>", 3), ("2,000>", 4)]
    controles = []
    for texto, nivel in niveles:
        controles.append(
            ft.Row(
                controls=[
                    ft.Container(width=8, height=8, border_radius=3,
                                  bgcolor=ft.Colors.with_opacity(ds.nivel_heatmap_a_opacidad(nivel), theme.PRIMARY)),
                    ft.Text(texto, size=10.5, color=theme.TEXT_MUTED),
                ],
                spacing=4, tight=True,
            )
        )
    return ft.Row(controls=controles, spacing=10)


def _celda(nivel: int) -> ft.Container:
    opacidad = ds.nivel_heatmap_a_opacidad(nivel)
    return ft.Container(
        width=_TAMAÑO_CELDA, height=_TAMAÑO_CELDA, border_radius=7,
        bgcolor=ft.Colors.with_opacity(opacidad, theme.PRIMARY) if opacidad > 0 else theme.CARD_BG_ALT,
    )


def heatmap_card(horas: list, dias: list, matriz: list) -> ft.Container:
    encabezado_dias = ft.Row(
        controls=[ft.Container(width=30)] + [
            ft.Container(content=ft.Text(d, size=11, color=theme.TEXT_MUTED), width=_TAMAÑO_CELDA,
                          alignment=ft.Alignment.CENTER)
            for d in dias
        ],
        spacing=6,
    )

    filas = [encabezado_dias]
    for i, hora in enumerate(horas):
        fila = ft.Row(
            controls=[
                ft.Container(content=ft.Text(hora, size=11, color=theme.TEXT_MUTED), width=30),
            ] + [_celda(matriz[j][i]) for j in range(len(dias))],
            spacing=6,
        )
        filas.append(fila)

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Pedidos por Hora", size=15.5, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY),
                        _leyenda(),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Column(controls=filas, spacing=6),
            ],
            spacing=18,
        ),
        bgcolor=theme.CARD_BG,
        border=ft.Border.all(1, theme.BORDER),
        border_radius=theme.CARD_RADIUS,
        padding=20,
        expand=True,
    )
