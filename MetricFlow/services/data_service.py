"""
services/data_service.py — Lógica pura (sin ft.*), testeable por consola.
"""


def formatear_delta(valor: float) -> str:
    signo = "+" if valor >= 0 else ""
    return f"{signo}{valor:.1f}%"


def color_por_estado_orden(estado: str) -> str:
    return {
        "Entregado": "success", "En camino": "info",
        "Procesando": "warning", "Cancelado": "danger",
    }.get(estado, "muted")


def nivel_heatmap_a_opacidad(nivel: int) -> float:
    return {0: 0.0, 1: 0.18, 2: 0.4, 3: 0.65, 4: 0.9}.get(nivel, 0.0)


def color_stock(stock: int) -> str:
    if stock == 0:
        return "danger"
    if stock < 20:
        return "warning"
    return "success"


def etiqueta_stock(stock: int) -> str:
    if stock == 0:
        return "Agotado"
    if stock < 20:
        return "Bajo stock"
    return "Disponible"
