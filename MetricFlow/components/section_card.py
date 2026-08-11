"""
components/section_card.py — Contenedor "card" estándar usado en todas
las vistas (fondo oscuro, bordes redondeados, borde sutil).
"""
import flet as ft
import theme


def section_card(content: ft.Control, padding: int = 20, expand=None) -> ft.Container:
    return ft.Container(
        content=content,
        bgcolor=theme.CARD_BG,
        border=ft.Border.all(1, theme.BORDER),
        border_radius=theme.CARD_RADIUS,
        padding=padding,
        expand=expand,
    )


def section_header(titulo: str, accion_texto: str = None, on_accion=None) -> ft.Row:
    controles = [ft.Text(titulo, size=15.5, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY)]
    fila = [controles[0]]
    if accion_texto:
        fila.append(
            ft.Container(
                content=ft.Text(accion_texto, size=12.5, weight=ft.FontWeight.W_600, color=theme.PRIMARY),
                on_click=on_accion, ink=True,
            )
        )
    return ft.Row(controls=fila, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
