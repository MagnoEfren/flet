"""
app.py
UI principal del dashboard industrial.
Single-page app con Tabs para cambiar entre vistas de gráficos.
"""

import flet as ft
 
from data_generator import DataGenerator
from charts import (
    build_linechart_temperatura,
    build_linechart_presion,
    build_linechart_vibracion,
    build_barchart_produccion,
    build_piechart_energia,
    build_scatterchart_correlacion,
)


# ── Constantes de diseño ──────────────────────────────────────────────────────
BG_APP          = "#0D1117"   # fondo oscuro principal
BG_CARD         = "#161B22"   # fondo de tarjetas
BG_HEADER       = "#1C2128"   # fondo del header
BORDER_COLOR    = "#30363D"   # borde sutil
ACCENT          = "#58A6FF"   # azul GitHub-like
TEXT_PRIMARY    = "#E6EDF3"
TEXT_SECONDARY  = "#8B949E"
RADIUS          = 12          # radio de bordes


def _tarjeta_kpi(icono: str, titulo: str, valor: str, unidad: str, color: str) -> ft.Container:
    """Tarjeta KPI compacta para el header."""
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(icono, color=color, size=22),
                    bgcolor=ft.Colors.with_opacity(0.12, color),
                    border_radius=8,
                    padding=ft.Padding(8, 8, 8, 8),
                ),
                ft.Column(
                    controls=[
                        ft.Text(titulo, size=11, color=TEXT_SECONDARY),
                        ft.Row(
                            controls=[
                                ft.Text(valor, size=18, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                                ft.Text(unidad, size=11, color=TEXT_SECONDARY),
                            ],
                            spacing=4,
                            vertical_alignment=ft.CrossAxisAlignment.END,
                        ),
                    ],
                    spacing=2,
                ),
            ],
            spacing=10,
        ),
        bgcolor=BG_CARD,
        border_radius=RADIUS,
        padding=ft.Padding(14, 12, 20, 12),
        border=ft.Border.all(1, BORDER_COLOR),
    )


def _seccion_grafico(titulo: str, subtitulo: str, grafico: ft.Control) -> ft.Container:
    """Contenedor visual estandarizado para cada gráfico."""
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(titulo, size=16, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Text(subtitulo, size=12, color=TEXT_SECONDARY),
                    ],
                    spacing=2,
                ),
                ft.Divider(color=BORDER_COLOR, thickness=1),
                ft.Container(
                    content=grafico,
                    height=340,
                    expand=True,
                ),
            ],
            spacing=12,
            expand=True,
        ),
        bgcolor=BG_CARD,
        border_radius=RADIUS,
        padding=ft.Padding(20, 18, 20, 18),
        border=ft.Border.all(1, BORDER_COLOR),
        expand=True,
    )


class DashboardApp:
    """Clase principal que construye y gestiona la UI del dashboard."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.data = DataGenerator()
        self._configurar_pagina()
        self._construir_ui()

    # ── Configuración de página ───────────────────────────────────────────────

    def _configurar_pagina(self):
        p = self.page
        p.title = "Industrial Dashboard Flet"
        p.bgcolor = BG_APP
        p.padding = ft.Padding(0, 0, 0, 0)
 
        p.theme = ft.Theme(color_scheme_seed=ACCENT)
        p.dark_theme = ft.Theme(color_scheme_seed=ACCENT)
        p.theme_mode = ft.ThemeMode.DARK

 

    def _construir_header(self) -> ft.Container:
        """Barra superior con título y KPIs."""
        d = self.data

        # Valores actuales (última lectura)
        temp_actual   = d.temperatura[-1]
        pres_actual   = d.presion[-1]
        vib_actual    = d.vibracion[-1]
        energia_total = round(sum(d.energia), 1)

        alerta_vib = vib_actual > 3.5

        kpis = ft.Row(
            controls=[
                _tarjeta_kpi(
                    ft.Icons.THERMOSTAT,
                    "Temperatura",
                    str(temp_actual), "°C",
                    ft.Colors.ORANGE_400,
                ),
                _tarjeta_kpi(
                    ft.Icons.COMPRESS,
                    "Presión",
                    str(pres_actual), "bar",
                    ft.Colors.CYAN_400,
                ),
                _tarjeta_kpi(
                    ft.Icons.VIBRATION,
                    "Vibración",
                    str(round(vib_actual, 2)), "mm/s",
                    ft.Colors.RED_400 if alerta_vib else ft.Colors.PURPLE_400,
                ),
                _tarjeta_kpi(
                    ft.Icons.BOLT,
                    "Energía hoy",
                    str(energia_total), "kWh",
                    ft.Colors.AMBER_400,
                ),
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        )

        titulo_row = ft.Row(
            controls=[
                ft.Icon(ft.Icons.FACTORY, color=ACCENT, size=26),
                ft.Column(
                    controls=[
                        ft.Text(
                            "INDUSTRIAL DASHBOARD",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_PRIMARY,
                        ),
                        ft.Text(
                            "Sistema de monitoreo de sensores — Planta A3",
                            size=12,
                            color=TEXT_SECONDARY,
                        ),
                    ],
                    spacing=2,
                ),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                width=8, height=8,
                                bgcolor=ft.Colors.GREEN_400,
                                border_radius=4,
                            ),
                            ft.Text("EN LÍNEA", size=11, color=ft.Colors.GREEN_400,
                                    weight=ft.FontWeight.BOLD),
                        ],
                        spacing=6,
                    ),
                    bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.GREEN_400),
                    border_radius=20,
                    padding=ft.Padding(10, 5, 10, 5),
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
        )

        return ft.Container(
            content=ft.Column(
                controls=[titulo_row, kpis],
                spacing=16,
            ),
            bgcolor=BG_HEADER,
            padding=ft.Padding(24, 18, 24, 18),
            border=ft.Border.only(bottom=ft.BorderSide(1, BORDER_COLOR)),
        )

    def _construir_tabs(self) -> ft.Tabs:
        """Tabs para seleccionar el tipo de gráfico.
        API actual: ft.Tabs > content: ft.Column > [ft.TabBar, ft.TabBarView]
        """
        d = self.data

        # ── Contenido de cada vista ───────────────────────────────

        # Vista 1: Temperatura (LineChart)
        vista_temperatura = ft.Container(
                content=ft.Column(
                    controls=[
                        _seccion_grafico(
                            "Temperatura del Horno — Últimas 24h",
                            "Sensor PT-100 · Rango operativo: 180–240 °C · Línea roja = límite de alerta",
                            build_linechart_temperatura(d),
                        ),
                    ],
                    expand=True,
                ),
                padding=ft.Padding(20, 16, 20, 16),
                expand=True,
        )

        # Vista 2: Presión (LineChart)
        vista_presion = ft.Container(
                content=ft.Column(
                    controls=[
                        _seccion_grafico(
                            "Presión Hidráulica — Últimas 24h",
                            "Sensor P-200 · Setpoint: 6.0 bar · Línea verde punteada = setpoint",
                            build_linechart_presion(d),
                        ),
                    ],
                    expand=True,
                ),
                padding=ft.Padding(20, 16, 20, 16),
                expand=True,
        )

        # Vista 3: Vibración (LineChart)
        vista_vibracion = ft.Container(
                content=ft.Column(
                    controls=[
                        _seccion_grafico(
                            "Vibración de Rodamientos — Últimas 24h",
                            "Sensor V-300 · Umbral de alerta: 3.5 mm/s RMS · Anomalía detectada ~hora 15:00",
                            build_linechart_vibracion(d),
                        ),
                    ],
                    expand=True,
                ),
                padding=ft.Padding(20, 16, 20, 16),
                expand=True,
        )

        # Vista 4: Producción (BarChart)
        vista_produccion = ft.Container(
                content=ft.Column(
                    controls=[
                        _seccion_grafico(
                            "Producción por Turno — Día 26/04/2026",
                            "Unidades acumuladas por turno (Mañana / Tarde / Noche)",
                            build_barchart_produccion(d),
                        ),
                    ],
                    expand=True,
                ),
                padding=ft.Padding(20, 16, 20, 16),
                expand=True,
        )

        # Vista 5: Energía (PieChart) — conserva el layout Row original
        vista_energia = ft.Container(
                content=ft.Row(
                    controls=[
                        # PieChart
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    _seccion_grafico(
                                        "Distribución Energética por Área",
                                        "Porcentaje de consumo eléctrico · Turno completo",
                                        build_piechart_energia(d),
                                    ),
                                ],
                                expand=True,
                            ),
                            expand=2,
                        ),
                        # Leyenda detallada
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        "Desglose de Consumo",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT_PRIMARY,
                                    ),
                                    ft.Divider(color=BORDER_COLOR),
                                    *[
                                        ft.Row(
                                            controls=[
                                                ft.Container(
                                                    width=12, height=12,
                                                    bgcolor=color,
                                                    border_radius=3,
                                                ),
                                                ft.Text(area, size=13, color=TEXT_PRIMARY, expand=True),
                                                ft.Text(f"{pct}%", size=13,
                                                        color=TEXT_SECONDARY,
                                                        weight=ft.FontWeight.W_600),
                                            ],
                                            spacing=8,
                                        )
                                        for (area, pct), color in zip(
                                            d.get_resumen_pie().items(),
                                            [
                                                ft.Colors.ORANGE_400,
                                                ft.Colors.BLUE_400,
                                                ft.Colors.AMBER_400,
                                                ft.Colors.CYAN_400,
                                                ft.Colors.PURPLE_400,
                                            ],
                                        )
                                    ],
                                    ft.Divider(color=BORDER_COLOR),
                                    ft.Text(
                                        f"Total: {round(sum(d.energia), 1)} kWh",
                                        size=13,
                                        color=TEXT_PRIMARY,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                                spacing=10,
                            ),
                            bgcolor=BG_CARD,
                            border_radius=RADIUS,
                            padding=ft.Padding(20, 18, 20, 18),
                            border=ft.Border.all(1, BORDER_COLOR),
                            expand=1,
                        ),
                    ],
                    spacing=16,
                    expand=True,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                padding=ft.Padding(20, 16, 20, 16),
                expand=True,
            )
        
        # Vista 6: Correlación (ScatterChart)
        vista_correlacion = ft.Container(
                content=ft.Column(
                    controls=[
                        _seccion_grafico(
                            "Correlación Energía vs Producción",
                            "ScatterChart · Cada punto = 30 min de operación · Análisis de eficiencia energética",
                            build_scatterchart_correlacion(d),
                        ),
                        ft.Container(
                            content=ft.Text(
                                "💡 Nota: Los puntos agrupados en la esquina inferior-izquierda corresponden al turno "
                                "nocturno con maquinaria detenida. El cluster central-superior es el turno de mayor eficiencia.",
                                size=12,
                                color=TEXT_SECONDARY,
                            ),
                            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLUE),
                            border_radius=8,
                            padding=ft.Padding(12, 10, 12, 10),
                            border=ft.Border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.BLUE)),
                        ),
                    ],
                    spacing=12,
                    expand=True,
                ),
                padding=ft.Padding(20, 16, 20, 16),
                expand=True,
        )

        # ── Ensamblado con TabBar + TabBarView (API actual) ───────
        return ft.Tabs(
            selected_index=0,
            expand=True,
            length=6,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        indicator_color=ACCENT,
                        label_color=ACCENT,
                        unselected_label_color=TEXT_SECONDARY,
                        label_text_style=ft.TextStyle(
                            weight=ft.FontWeight.BOLD,
                            size=13,
                        ),
                        unselected_label_text_style=ft.TextStyle(
                            weight=ft.FontWeight.W_400,
                            size=13,
                        ),
                        overlay_color=ft.Colors.with_opacity(0.08, ACCENT),
                        divider_color="transparent",
                        tabs=[
                            ft.Tab(label="Temperatura"),
                            ft.Tab(label="Presión"),
                            ft.Tab(label="Vibración"),
                            ft.Tab(label="Producción"),
                            ft.Tab(label="Energía"),
                            ft.Tab(label="Eficiencia"),
                        ],
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            vista_temperatura,
                            vista_presion,
                            vista_vibracion,
                            vista_produccion,
                            vista_energia,
                            vista_correlacion,
                        ],
                    ),
                ],
            ),
        )

    def _construir_ui(self):
        """Ensambla todos los componentes en la página."""
        header = self._construir_header()
        tabs   = self._construir_tabs()

        self.page.add(
            ft.Column(
                controls=[
                    header,
                    ft.Container(
                        content=tabs,
                        expand=True,
                    ),
                ],
                spacing=0,
                expand=True,
            )
        )
        self.page.update()