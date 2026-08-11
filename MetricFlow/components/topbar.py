"""
components/topbar.py — Barra superior: buscador, fecha, notificaciones y avatar.
"""
import flet as ft
import theme


def topbar(fecha_texto: str, iniciales_usuario: str = "CM") -> ft.Container:
    buscador = ft.TextField(
        hint_text="Buscar",
        hint_style=ft.TextStyle(color=theme.TEXT_MUTED),
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        color=theme.TEXT_PRIMARY,
        bgcolor=theme.INPUT_BG, fill_color=theme.INPUT_BG, filled=True,
        border=ft.InputBorder.NONE, border_radius=12,
        content_padding=ft.Padding.symmetric(horizontal=6, vertical=10),
        text_size=13.5,
        width=340,
    )

    chip_fecha = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.CALENDAR_TODAY_ROUNDED, size=15, color=theme.TEXT_SECONDARY),
                ft.Text(fecha_texto, size=13, color=theme.TEXT_SECONDARY),
            ],
            spacing=8,
        ),
        bgcolor=theme.CARD_BG_ALT,
        border=ft.Border.all(1, theme.BORDER),
        border_radius=theme.PILL_RADIUS,
        padding=ft.Padding.symmetric(horizontal=14, vertical=9),
    )

    notificaciones = ft.Stack(
        controls=[
            ft.Container(
                content=ft.Icon(ft.Icons.NOTIFICATIONS_NONE_ROUNDED, size=20, color=theme.TEXT_SECONDARY),
                width=38, height=38, border_radius=999, bgcolor=theme.CARD_BG_ALT,
                border=ft.Border.all(1, theme.BORDER), alignment=ft.Alignment.CENTER,
            ),
            ft.Container(width=8, height=8, border_radius=99, bgcolor=theme.PRIMARY,
                          right=6, top=6),
        ],
        width=38, height=38,
    )

    avatar = ft.Container(
        content=ft.Text(iniciales_usuario, size=13, weight=ft.FontWeight.W_700, color="#0E1116"),
        width=38, height=38, border_radius=999,
        bgcolor=theme.PRIMARY, alignment=ft.Alignment.CENTER,
    )

    return ft.Container(
        content=ft.Row(
            controls=[
                buscador,
                ft.Row(controls=[chip_fecha, notificaciones, avatar], spacing=14),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.Padding.only(left=28, right=28, top=22, bottom=6),
    )
