"""
components/metric_card.py — Tarjeta de métrica superior del dashboard:
título + badge de variación arriba, valor grande abajo, rango de fechas chico.
"""
import flet as ft
import theme
from services import data_service as ds

_COLORES = {"success": theme.SUCCESS, "danger": theme.DANGER}


def _badge_delta(delta: float, positivo: bool) -> ft.Container:
    color = _COLORES["success"] if positivo else _COLORES["danger"]
    icono = ft.Icons.TRENDING_UP_ROUNDED if positivo else ft.Icons.TRENDING_DOWN_ROUNDED
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(icono, size=12, color=color),
                ft.Text(ds.formatear_delta(delta), size=11.5, weight=ft.FontWeight.W_700, color=color),
            ],
            spacing=3, tight=True,
        ),
        bgcolor=ft.Colors.with_opacity(0.14, color),
        padding=ft.Padding.symmetric(horizontal=8, vertical=4),
        border_radius=theme.PILL_RADIUS,
    )


def metric_card(titulo: str, valor: str, delta: float, positivo: bool, subtitulo: str = None) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(titulo, size=13, color=theme.TEXT_SECONDARY),
                        _badge_delta(delta, positivo),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(valor, size=26, weight=ft.FontWeight.W_800, color=theme.TEXT_PRIMARY),
                ft.Text(subtitulo, size=11, color=theme.TEXT_MUTED) if subtitulo else ft.Container(),
            ],
            spacing=10,
        ),
        bgcolor=theme.CARD_BG,
        border=ft.Border.all(1, theme.BORDER),
        border_radius=theme.CARD_RADIUS,
        padding=18,
        expand=True,
    )
