"""
components/growth_indicator.py — Texto con flecha de crecimiento
(sin fondo de pill), usado en columnas de tablas tipo "Crecimiento".
"""
import flet as ft
import theme


def growth_indicator(valor: float) -> ft.Row:
    positivo = valor >= 0
    color = theme.SUCCESS if positivo else theme.DANGER
    icono = ft.Icons.ARROW_OUTWARD_ROUNDED if positivo else ft.Icons.SOUTH_EAST_ROUNDED
    signo = "+" if positivo else ""
    return ft.Row(
        controls=[
            ft.Icon(icono, size=12, color=color),
            ft.Text(f"{signo}{valor:.0f}%", size=12.5, weight=ft.FontWeight.W_700, color=color),
        ],
        spacing=3, tight=True,
    )
