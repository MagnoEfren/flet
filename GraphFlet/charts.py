"""
charts.py
Fábrica de gráficos industriales usando flet_charts (flet-charts).
Todos los componentes verificados en:  

Disponibles en flet_charts:
  ✅ LineChart     → Temperatura / Presión / Vibración
  ✅ BarChart      → Producción por turno
  ✅ PieChart      → Distribución energética
  ✅ ScatterChart  → Energía vs Producción (correlación)
  ❌ AreaChart     → NO EXISTE en flet_charts actual.
                     Reemplazado por ScatterChart (correlación energía-producción).
"""

import flet as ft
import flet_charts as fch
from data_generator import DataGenerator


# ── Paleta de colores corporativa ────────────────────────────────────────────
C_AZUL      = ft.Colors.BLUE_400
C_CYAN      = ft.Colors.CYAN_400
C_VERDE     = ft.Colors.GREEN_400
C_NARANJA   = ft.Colors.ORANGE_400
C_ROJO      = ft.Colors.RED_400
C_PURPURA   = ft.Colors.PURPLE_400
C_AMARILLO  = ft.Colors.AMBER_400
C_FONDO     = ft.Colors.with_opacity(0.05, ft.Colors.WHITE)


def _eje_x_horas(timestamps: list[str], paso: int = 4) -> fch.ChartAxis:
    """Genera etiquetas para el eje X con marcas cada `paso` puntos."""
    labels = []
    for i, ts in enumerate(timestamps):
        if i % paso == 0:
            labels.append(
                fch.ChartAxisLabel(
                    value=i,
                    label=ft.Text(ts, size=9, color=ft.Colors.GREY_400),
                )
            )
    return fch.ChartAxis(labels=labels, label_size=32)


def _eje_y(titulo: str, min_v: float, max_v: float, pasos: int = 5) -> fch.ChartAxis:
    """Eje Y con etiquetas numéricas uniformes."""
    rango = max_v - min_v
    labels = []
    for i in range(pasos + 1):
        val = round(min_v + rango * i / pasos, 1)
        labels.append(
            fch.ChartAxisLabel(
                value=val,
                label=ft.Text(str(val), size=9, color=ft.Colors.GREY_400),
            )
        )
    return fch.ChartAxis(labels=labels, label_size=48, title=ft.Text(titulo, size=10))


# ─────────────────────────────────────────────────────────────────────────────
# 1. LineChart — Temperatura
# ─────────────────────────────────────────────────────────────────────────────

def build_linechart_temperatura(data: DataGenerator) -> fch.LineChart:
    ts = data.get_timestamps_str()
    vals = data.temperatura
    n = len(vals)

    puntos = [fch.LineChartDataPoint(i, v) for i, v in enumerate(vals)]

    serie = fch.LineChartData(
        color=C_NARANJA,
        stroke_width=2.5,
        curved=True,
        rounded_stroke_cap=True,
        points=puntos,
        below_line_gradient=ft.LinearGradient(
            begin=ft.Alignment(0, -1),
            end=ft.Alignment(0, 1),
            colors=[
                ft.Colors.with_opacity(0.35, C_NARANJA),
                ft.Colors.with_opacity(0.0, C_NARANJA),
            ],
        ),
    )

    # Línea de límite superior (alerta)
    limite = fch.LineChartData(
        color=ft.Colors.with_opacity(0.5, C_ROJO),
        stroke_width=1,
        curved=False,
        dash_pattern=[6, 4],
        points=[fch.LineChartDataPoint(0, 235), fch.LineChartDataPoint(n - 1, 235)],
    )

    return fch.LineChart(
        data_series=[serie, limite],
        min_x=0,
        max_x=n - 1,
        min_y=170,
        max_y=250,
        interactive=True,
        bgcolor=C_FONDO,
        left_axis=_eje_y("°C", 170, 250),
        bottom_axis=_eje_x_horas(ts),
        horizontal_grid_lines=fch.ChartGridLines(
            interval=20, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)
        ),
        expand=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 2. LineChart — Presión
# ─────────────────────────────────────────────────────────────────────────────

def build_linechart_presion(data: DataGenerator) -> fch.LineChart:
    ts = data.get_timestamps_str()
    vals = data.presion
    n = len(vals)

    puntos = [fch.LineChartDataPoint(i, v) for i, v in enumerate(vals)]

    serie = fch.LineChartData(
        color=C_CYAN,
        stroke_width=2.5,
        curved=True,
        rounded_stroke_cap=True,
        points=puntos,
        below_line_gradient=ft.LinearGradient(
            begin=ft.Alignment(0, -1),
            end=ft.Alignment(0, 1),
            colors=[
                ft.Colors.with_opacity(0.3, C_CYAN),
                ft.Colors.with_opacity(0.0, C_CYAN),
            ],
        ),
    )

    setpoint = fch.LineChartData(
        color=ft.Colors.with_opacity(0.4, C_VERDE),
        stroke_width=1,
        dash_pattern=[8, 4],
        points=[fch.LineChartDataPoint(0, 6.0), fch.LineChartDataPoint(n - 1, 6.0)],
    )

    return fch.LineChart(
        data_series=[serie, setpoint],
        min_x=0,
        max_x=n - 1,
        min_y=3.5,
        max_y=8.5,
        interactive=True,
        bgcolor=C_FONDO,
        left_axis=_eje_y("bar", 3.5, 8.5),
        bottom_axis=_eje_x_horas(ts),
        horizontal_grid_lines=fch.ChartGridLines(
            interval=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)
        ),
        expand=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 3. LineChart — Vibración (con zona de alerta visual)
# ─────────────────────────────────────────────────────────────────────────────

def build_linechart_vibracion(data: DataGenerator) -> fch.LineChart:
    ts = data.get_timestamps_str()
    vals = data.vibracion
    n = len(vals)

    puntos = [fch.LineChartDataPoint(i, v) for i, v in enumerate(vals)]

    serie = fch.LineChartData(
        color=C_PURPURA,
        stroke_width=2.5,
        curved=True,
        rounded_stroke_cap=True,
        points=puntos,
        below_line_gradient=ft.LinearGradient(
            begin=ft.Alignment(0, -1),
            end=ft.Alignment(0, 1),
            colors=[
                ft.Colors.with_opacity(0.3, C_PURPURA),
                ft.Colors.with_opacity(0.0, C_PURPURA),
            ],
        ),
    )

    umbral = fch.LineChartData(
        color=ft.Colors.with_opacity(0.6, C_ROJO),
        stroke_width=1.5,
        dash_pattern=[5, 3],
        points=[fch.LineChartDataPoint(0, 3.5), fch.LineChartDataPoint(n - 1, 3.5)],
    )

    return fch.LineChart(
        data_series=[serie, umbral],
        min_x=0,
        max_x=n - 1,
        min_y=0,
        max_y=5.5,
        interactive=True,
        bgcolor=C_FONDO,
        left_axis=_eje_y("mm/s", 0, 5.5),
        bottom_axis=_eje_x_horas(ts),
        horizontal_grid_lines=fch.ChartGridLines(
            interval=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)
        ),
        expand=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 4. BarChart — Producción por turno
# ─────────────────────────────────────────────────────────────────────────────

def build_barchart_produccion(data: DataGenerator) -> fch.BarChart:
    turnos = data.get_produccion_por_turno()
    colores = [C_AZUL, C_VERDE, C_PURPURA]
    etiquetas = list(turnos.keys())
    valores = list(turnos.values())
    max_val = max(valores) * 1.2

    grupos = []
    for i, (etiqueta, valor) in enumerate(zip(etiquetas, valores)):
        grupos.append(
            fch.BarChartGroup(
                x=i,
                rods=[
                    fch.BarChartRod(
                        from_y=0,
                        to_y=valor,
                        width=40,
                        color=colores[i],
                        border_radius=ft.BorderRadius(6, 6, 0, 0),
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment(0, -1),
                            end=ft.Alignment(0, 1),
                            colors=[
                                ft.Colors.with_opacity(1.0, colores[i]),
                                ft.Colors.with_opacity(0.6, colores[i]),
                            ],
                        ),
                        tooltip=f"{etiqueta}: {valor} uds",
                    )
                ],
            )
        )

    eje_x = fch.ChartAxis(
        labels=[
            fch.ChartAxisLabel(
                value=i,
                label=ft.Text(etiquetas[i], size=12, weight=ft.FontWeight.W_600),
            )
            for i in range(len(etiquetas))
        ],
        label_size=40,
    )

    eje_y = fch.ChartAxis(
        labels=[
            fch.ChartAxisLabel(
                value=v,
                label=ft.Text(str(int(v)), size=9, color=ft.Colors.GREY_400),
            )
            for v in [0, 500, 1000, 1500, 2000, int(max_val)]
        ],
        label_size=50,
    )

    return fch.BarChart(
        groups=grupos,
        group_spacing=24,
        max_y=max_val,
        interactive=True,
        bgcolor=C_FONDO,
        bottom_axis=eje_x,
        left_axis=eje_y,
        horizontal_grid_lines=fch.ChartGridLines(
            interval=500, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)
        ),
        expand=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 5. PieChart — Distribución energética por área
# ─────────────────────────────────────────────────────────────────────────────

def build_piechart_energia(data: DataGenerator) -> fch.PieChart:
    resumen = data.get_resumen_pie()
    colores = [C_NARANJA, C_AZUL, C_AMARILLO, C_CYAN, C_PURPURA]

    secciones = []
    for (nombre, pct), color in zip(resumen.items(), colores):
        secciones.append(
            fch.PieChartSection(
                value=pct,
                color=color,
                radius=110,
                title=f"{nombre}\n{pct}%",
                title_style=ft.TextStyle(
                    size=11,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.WHITE,
                ),
                badge=ft.Container(
                    content=ft.Text(f"{pct:.1f}%", size=9, color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.with_opacity(0.4, ft.Colors.BLACK),
                    border_radius=8,
                    padding=ft.Padding(4, 2, 4, 2),
                ),
                badge_position=0.98,
            )
        )

    return fch.PieChart(
        sections=secciones,
        sections_space=3,
        center_space_radius=50,
     #   interactive=True,
        expand=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 6. ScatterChart — Correlación Energía vs Producción
#    (Reemplaza al AreaChart que NO existe en flet_charts actual)
# ─────────────────────────────────────────────────────────────────────────────

def build_scatterchart_correlacion(data: DataGenerator) -> fch.ScatterChart:
    """
    Muestra la relación entre consumo energético (kWh) y producción (uds/h).
    Útil para análisis de eficiencia energética.
    """
    
    puntos = []
    for e, p in zip(data.energia, data.produccion):
        puntos.append(
            fch.ScatterChartSpot(
                x=e,
                y=p,
                radius=5,
                color=ft.Colors.with_opacity(0.75, C_VERDE),
            )
        )

    return fch.ScatterChart(
        spots=puntos,
        min_x=25,
        max_x=110,
        min_y=0,
        max_y=200,
        interactive=True,
        bgcolor=C_FONDO,
        left_axis=fch.ChartAxis(
            labels=[
                fch.ChartAxisLabel(
                    value=v,
                    label=ft.Text(str(v), size=9, color=ft.Colors.GREY_400),
                )
                for v in [0, 50, 100, 150, 200]
            ],
            label_size=46,
            title=ft.Text("Producción (uds/h)", size=10),
        ),
        bottom_axis=fch.ChartAxis(
            labels=[
                fch.ChartAxisLabel(
                    value=v,
                    label=ft.Text(str(v), size=9, color=ft.Colors.GREY_400),
                )
                for v in [30, 50, 70, 90, 110]
            ],
            label_size=32,
            title=ft.Text("Energía (kWh)", size=10),
        ),
        horizontal_grid_lines=fch.ChartGridLines(
            interval=50, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)
        ),
        vertical_grid_lines=fch.ChartGridLines(
            interval=20, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)
        ),
        expand=True,
    )
