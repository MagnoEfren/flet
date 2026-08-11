"""
components/status_badge.py — Badge de estado genérico reutilizable.
"""
import flet as ft
import theme

_COLORES = {
    "success": theme.SUCCESS, "danger": theme.DANGER,
    "warning": "#F5A623", "info": theme.ACCENT_BLUE, "muted": theme.TEXT_MUTED,
}


def status_badge(texto: str, tono: str = "muted") -> ft.Container:
    color = _COLORES.get(tono, theme.TEXT_MUTED)
    return ft.Container(
        content=ft.Text(texto, size=11.5, weight=ft.FontWeight.W_700, color=color),
        bgcolor=ft.Colors.with_opacity(0.14, color),
        padding=ft.Padding.symmetric(horizontal=10, vertical=5),
        border_radius=theme.PILL_RADIUS,
    )
