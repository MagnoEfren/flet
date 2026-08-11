"""
views/settings_view.py — Pantalla "Ajustes": perfil y preferencias.
"""
import flet as ft
import theme
from components.section_card import section_card, section_header


class SettingsView(ft.Container):
    def __init__(self, estado, mostrar_snack):
        super().__init__()
        self.estado = estado
        self.mostrar_snack = mostrar_snack
        self.expand = True
        self.padding = ft.Padding.only(left=28, right=28, top=14, bottom=28)
        self.notif_pedidos = True
        self.notif_marketing = False
        self.modo_compacto = False

    def refrescar(self):
        e = self.estado
        encabezado = ft.Text("Ajustes", size=22, weight=ft.FontWeight.W_800, color=theme.TEXT_PRIMARY)

        tarjeta_perfil = section_card(
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text("".join([p[0] for p in e.usuario_nombre.split()[:2]]),
                                          size=18, weight=ft.FontWeight.W_800, color="#0E1116"),
                        width=56, height=56, border_radius=999,
                        bgcolor=theme.PRIMARY, alignment=ft.Alignment.CENTER,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(e.usuario_nombre, size=15.5, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY),
                            ft.Text(e.usuario_rol, size=12.5, color=theme.TEXT_SECONDARY),
                        ],
                        spacing=2,
                    ),
                ],
                spacing=16,
            )
        )

        campos = section_card(
            ft.Column(
                controls=[
                    section_header("Información de la cuenta"),
                    self._campo("Nombre completo", e.usuario_nombre),
                    self._campo("Rol", e.usuario_rol),
                    self._campo("Correo", "carlos.medina@metricflow.com"),
                ],
                spacing=14,
            )
        )

        preferencias = section_card(
            ft.Column(
                controls=[
                    section_header("Preferencias"),
                    self._fila_switch("Notificaciones de pedidos", self.notif_pedidos, "notif_pedidos"),
                    self._fila_switch("Notificaciones de marketing", self.notif_marketing, "notif_marketing"),
                    self._fila_switch("Modo compacto", self.modo_compacto, "modo_compacto"),
                ],
                spacing=18,
            )
        )

        self.content = ft.Column(
            controls=[encabezado, tarjeta_perfil, campos, preferencias],
            spacing=18,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _campo(self, etiqueta: str, valor: str) -> ft.Column:
        return ft.Column(
            controls=[
                ft.Text(etiqueta, size=12, color=theme.TEXT_SECONDARY),
                ft.Container(
                    content=ft.Text(valor, size=13.5, color=theme.TEXT_PRIMARY),
                    bgcolor=theme.CARD_BG_ALT, border_radius=10,
                    padding=ft.Padding.symmetric(horizontal=14, vertical=12),
                ),
            ],
            spacing=6,
        )

    def _fila_switch(self, etiqueta: str, valor: bool, atributo: str) -> ft.Row:
        return ft.Row(
            controls=[
                ft.Text(etiqueta, size=13.5, color=theme.TEXT_PRIMARY),
                ft.Switch(value=valor, active_color=theme.PRIMARY, data=atributo,
                           on_change=self._al_cambiar_switch),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def _al_cambiar_switch(self, e):
        setattr(self, e.control.data, e.control.value)
        self.mostrar_snack("Preferencias actualizadas.", theme.PRIMARY)
