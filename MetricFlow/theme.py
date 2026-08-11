"""
theme.py — Paleta de colores y constantes visuales de "Metric Flow".
Réplica del diseño de referencia (dashboard oscuro tipo SaaS), cambiando
únicamente el acento naranja original por un verde claro. El resto de
colores (fondo, tarjetas, texto, verde/rojo de variación) se mantiene.
"""

# --- Fondo ---
BG = "#0E1116"                  # fondo del panel principal
SIDEBAR_BG = "#0B0D12"          # fondo de la barra lateral (un poco más oscuro)
CARD_BG = "#181B22"             # tarjetas
CARD_BG_ALT = "#20242D"         # elementos anidados (filas de tabla, tiles, inputs)
INPUT_BG = "#181B22"
BORDER = "#262B35"              # bordes sutiles

# --- Acento principal (antes naranja -> ahora verde claro) ---
PRIMARY = "#7CE38B"              # verde claro — logo, item activo del menú, línea "Ventas"
PRIMARY_SOFT = "#7CE38B"         # variante para fondos translúcidos (misma base, se usa con opacidad)
PRIMARY_DARK = "#3FAE63"

# --- Semáforo (igual que el original, no es el color que se pidió cambiar) ---
SUCCESS = "#4ADE80"              # variaciones positivas (+12.5%, etc.)
DANGER = "#F87171"               # variaciones negativas (-4.3%, etc.)
ACCENT_BLUE = "#8B93F8"          # línea "Meta" del gráfico, detalles secundarios

# --- Texto ---
TEXT_PRIMARY = "#F3F4F6"
TEXT_SECONDARY = "#9CA3AF"
TEXT_MUTED = "#6B7280"

# --- Tipografía ---
FONT_FAMILY = None  # fuente del sistema/plataforma

# --- Layout ---
SIDEBAR_WIDTH = 232
CARD_RADIUS = 18
TILE_RADIUS = 14
PILL_RADIUS = 999
