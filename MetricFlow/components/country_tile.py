"""
components/country_tile.py — Tile de país (bandera + nombre + cantidad)
para la tarjeta "Ventas por País" del dashboard.
"""
import flet as ft
import theme


def country_tile(bandera: str, pais: str, productos: str) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(bandera, size=20),
                ft.Text(pais, size=12.5, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY),
                ft.Text(f"{productos} Productos", size=11, color=theme.TEXT_MUTED),
            ],
            spacing=4,
        ),
        bgcolor=theme.CARD_BG_ALT,
        border_radius=theme.TILE_RADIUS,
        padding=14,
        expand=True,
    )
