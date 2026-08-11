"""
components/sidebar.py — Barra lateral de navegación (estilo dashboard
desktop), con logo, ítems de menú y "Ajustes" fijo abajo.
"""
import flet as ft
import theme

ITEMS = [
    {"clave": "dashboard", "label": "Dashboard", "icon": ft.Icons.HOME_ROUNDED},
    {"clave": "ordenes", "label": "Órdenes", "icon": ft.Icons.RECEIPT_LONG_ROUNDED},
    {"clave": "productos", "label": "Productos", "icon": ft.Icons.INVENTORY_2_ROUNDED},
    {"clave": "clientes", "label": "Clientes", "icon": ft.Icons.PEOPLE_ALT_ROUNDED},
    {"clave": "analitica", "label": "Analítica", "icon": ft.Icons.BAR_CHART_ROUNDED},
]


def _logo() -> ft.Row:
    return ft.Row(
        controls=[
            ft.Container(
                content=ft.Icon(ft.Icons.INSIGHTS_ROUNDED, size=20, color="#0E1116"),
                width=38, height=38, border_radius=12,
                bgcolor=theme.PRIMARY, alignment=ft.Alignment.CENTER,
            ),
            ft.Text("Metric Flow", size=16.5, weight=ft.FontWeight.W_800, color=theme.TEXT_PRIMARY),
        ],
        spacing=10,
    )


def _nav_item(clave: str, label: str, icon: str, activo: bool, on_click) -> ft.Container:
    color = theme.PRIMARY if activo else theme.TEXT_SECONDARY
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(icon, size=18, color=color),
                ft.Text(label, size=13.5, weight=ft.FontWeight.W_700 if activo else ft.FontWeight.W_500,
                         color=color),
            ],
            spacing=12,
        ),
        padding=ft.Padding.symmetric(horizontal=14, vertical=11),
        border_radius=theme.TILE_RADIUS,
        bgcolor=ft.Colors.with_opacity(0.14, theme.PRIMARY) if activo else None,
        data=clave,
        on_click=on_click,
        ink=True,
        animate=ft.Animation(150),
    )


def sidebar(pestaña_activa: str, on_select) -> ft.Container:
    items_nav = [
        _nav_item(i["clave"], i["label"], i["icon"], i["clave"] == pestaña_activa, on_select)
        for i in ITEMS
    ]
    ajustes = _nav_item("ajustes", "Ajustes", ft.Icons.SETTINGS_ROUNDED, pestaña_activa == "ajustes", on_select)

    return ft.Container(
        content=ft.Column(
            controls=[
                _logo(),
                ft.Container(height=14),
                ft.Column(controls=items_nav, spacing=4),
                ft.Container(expand=True),
                ft.Container(content=ft.Divider(color=theme.BORDER, height=1)),
                ajustes,
            ],
            expand=True,
        ),
        width=theme.SIDEBAR_WIDTH,
        bgcolor=theme.SIDEBAR_BG,
        padding=ft.Padding.symmetric(horizontal=16, vertical=22),
        border=ft.Border(right=ft.BorderSide(1, theme.BORDER)),
    )
