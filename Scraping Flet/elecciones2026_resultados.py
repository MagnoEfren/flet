

"""
╔══════════════════════════════════════════════════════════╗
║   RESULTADOS ELECCIONES PRESIDENCIALES PERÚ 2026         ║
║   Fuente: resultadoelectoral.onpe.gob.pe                 ║
║   3 col × 4 filas · Panel actas · votos · ONPE oficial  ║
╚══════════════════════════════════════════════════════════╝

Instalar (una sola vez):
    pip install flet playwright
    playwright install chromium

Ejecutar:
    python elecciones2026_resultados.py

Si quieres ver qué JSON exacto devuelve ONPE, ejecuta primero:
    python debug_onpe.py
"""

import flet as ft
import threading
import time
import re
import json
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_OK = True
except ImportError:
    PLAYWRIGHT_OK = False

URL_ONPE  = "https://resultadoelectoral.onpe.gob.pe/main/resumen"
TOTAL_ACTAS_FIJO = 92_766          # Total oficial ONPE EG 2026
INTERVALO = 45                      # segundos entre actualizaciones

COLORES = [
    "#E53935", "#1E88E5", "#43A047", "#FB8C00", "#8E24AA",
    "#00ACC1", "#F4511E", "#6D4C41", "#039BE5", "#00897B",
    "#C0CA33", "#FFB300", "#D81B60", "#3949AB", "#546E7A",
]

# ═══════════════════════════════════════════════════════════
#  SCRAPER
# ═══════════════════════════════════════════════════════════

def _numero(txt) -> int:
    """Convierte '1,208' o '1.208' o '1208' a int."""
    try:
        s = str(txt).replace(" ", "").replace(",", "").replace(".", "")
        return int(s)
    except Exception:
        return 0

def _pct(txt) -> float:
    try:
        return float(str(txt).replace(",", ".").replace("%", "").strip())
    except Exception:
        return 0.0

# ── Parsear JSON capturado de la API interna ──────────────────────────────────
def _buscar_en_json(obj, profundidad=0):
    """
    Recorre recursivamente el JSON buscando lista de candidatos.
    Prueba decenas de nombres de campo que ONPE podría usar.
    Devuelve (candidatos[], actas_procesadas, actas_jee, total_actas).
    """
    candidatos = []
    actas_proc = 0
    actas_jee  = 0
    total      = 0

    if profundidad > 8 or not isinstance(obj, (dict, list)):
        return candidatos, actas_proc, actas_jee, total

    if isinstance(obj, dict):
        # ── Intentar extraer estadísticas de actas ──
        for k, v in obj.items():
            kl = k.lower()
            if any(x in kl for x in ["totalactas", "total_actas", "totalacta", "numactas"]):
                total = _numero(v) or total
            if any(x in kl for x in ["contabilizadas", "procesadas", "computadas", "actas_comp"]):
                actas_proc = _numero(v) or actas_proc
            if any(x in kl for x in ["jee", "enviojee", "envio_jee", "paraenvio"]):
                actas_jee = _numero(v) or actas_jee

        # ── Buscar lista de candidatos por nombre de clave ──
        claves_cands = [
            "candidatos", "candidates", "lista", "items", "resultados",
            "listaResultados", "listaCandidatos", "formulaPresidencial",
            "plancha", "organizaciones", "partidos", "datos",
        ]
        for clave in claves_cands:
            if clave in obj and isinstance(obj[clave], list) and len(obj[clave]) > 0:
                cands = _parsear_lista(obj[clave])
                if cands:
                    candidatos = cands
                    break

        # Si no encontramos, seguir buscando recursivamente
        if not candidatos:
            for v in obj.values():
                c, ap, aj, t = _buscar_en_json(v, profundidad + 1)
                if c:
                    candidatos = c
                if ap:
                    actas_proc = ap
                if aj:
                    actas_jee = aj
                if t:
                    total = t

    elif isinstance(obj, list):
        # Si la lista tiene dicts con campos de candidato, parsearla directo
        cands = _parsear_lista(obj)
        if cands:
            candidatos = cands
        else:
            for item in obj:
                c, ap, aj, t = _buscar_en_json(item, profundidad + 1)
                if c:
                    candidatos = c
                if ap:
                    actas_proc = ap
                if aj:
                    actas_jee = aj
                if t:
                    total = t

    return candidatos, actas_proc, actas_jee, total


def _parsear_lista(lst: list) -> list:
    """Convierte una lista JSON en candidatos si tiene los campos esperados."""
    resultado = []
    CAMPOS_NOMBRE = [
        "nombreCandidato", "nombre", "candidato", "nombrePostulante",
        "nomCandidato", "candidatNombre", "apellidos", "nombreCompleto",
        "denominacion", "nomOrganizacion", "nombreOrganizacion",
    ]
    CAMPOS_PARTIDO = [
        "organizacion", "partido", "nombreOrganizacion", "sigla",
        "nomOrganizacion", "agrupacion", "org",
    ]
    CAMPOS_VOTOS = [
        "totalVotos", "votos", "cantidadVotos", "numVotos",
        "votosValidos", "totalVotosValidos", "cant_votos",
        "cantVotos", "nroVotos",
    ]
    CAMPOS_PCT = [
        "porcentajeVotosValidos", "porcentaje", "pct",
        "porcentajeVotos", "porcentajeVotosEmitidos",
        "pctVotos", "porcentajeTotal", "porcentajeValidos",
    ]

    for item in lst:
        if not isinstance(item, dict):
            continue
        nombre = ""
        for k in CAMPOS_NOMBRE:
            if k in item and item[k]:
                nombre = str(item[k]).strip()
                break
        partido = ""
        for k in CAMPOS_PARTIDO:
            if k in item and item[k] and str(item[k]) != nombre:
                partido = str(item[k]).strip()
                break
        votos = 0
        for k in CAMPOS_VOTOS:
            if k in item:
                votos = _numero(item[k])
                if votos > 0:
                    break
        pct = 0.0
        for k in CAMPOS_PCT:
            if k in item:
                pct = _pct(item[k])
                if pct > 0:
                    break

        if nombre and (pct > 0 or votos > 0):
            resultado.append({
                "nombre":    nombre[:70],
                "partido":   partido[:60],
                "votos":     votos,
                "porcentaje": pct,
            })

    return resultado


# ── Parsear DOM renderizado por Playwright ────────────────────────────────────
def _parsear_dom(pg) -> tuple:
    """
    Extrae datos del DOM HTML ya renderizado.
    Retorna (candidatos, actas_proc, actas_jee, total_actas).
    """
    candidatos = []
    actas_proc = 0
    actas_jee  = 0
    total      = 0

    # 1) Filas de tabla
    try:
        filas = pg.query_selector_all("table tr, tbody tr")
        for fila in filas[:50]:
            celdas = [c.inner_text().strip() for c in fila.query_selector_all("td")]
            if len(celdas) < 2:
                continue
            nombre = celdas[0]
            if len(nombre) < 4 or nombre.lower() in ("candidato", "nombre", "partido", "total"):
                continue
            votos = 0
            pct   = 0.0
            for celda in celdas[1:]:
                # ¿Es porcentaje?
                m = re.search(r'(\d{1,2}[,\.]\d{2,4})\s*%?$', celda)
                if m and not pct:
                    v = _pct(m.group(1))
                    if 0 < v <= 100:
                        pct = v
                        continue
                # ¿Es votos (número > 0)?
                m2 = re.search(r'^[\d,\.]+$', celda.replace(" ", ""))
                if m2 and not votos:
                    n = _numero(celda)
                    if n > 0:
                        votos = n
            if pct > 0 or votos > 0:
                candidatos.append({
                    "nombre": nombre[:70], "partido": "",
                    "votos": votos, "porcentaje": pct,
                })
    except Exception:
        pass

    # 2) Regex sobre texto completo si tabla no dio nada
    if not candidatos:
        try:
            texto = pg.inner_text("body")
            # Patrón: NOMBRE [votos] porcentaje%
            bloques = re.findall(
                r'([A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜa-záéíóúñü\s,\.\-]{4,60}?)\s+'
                r'([\d,\.]{1,12})\s+'
                r'(\d{1,2}[,\.]\d{2,4})\s*%',
                texto
            )
            vistos = set()
            for nombre, votos_txt, pct_txt in bloques:
                nombre = nombre.strip()
                clave  = nombre.lower()
                if clave in vistos or len(nombre) < 5:
                    continue
                vistos.add(clave)
                p = _pct(pct_txt)
                v = _numero(votos_txt)
                if 0 < p <= 100:
                    candidatos.append({
                        "nombre": nombre[:70], "partido": "",
                        "votos": v, "porcentaje": p,
                    })
        except Exception:
            pass

    # 3) Extraer actas del texto
    try:
        texto = pg.inner_text("body")
        # Total actas
        m = re.search(r'total\s*(?:de)?\s*actas?\s*:?\s*([\d,\.]+)', texto, re.I)
        if m:
            total = _numero(m.group(1)) or TOTAL_ACTAS_FIJO

        # Contabilizadas / procesadas
        m2 = re.search(
            r'(?:contabilizadas?|procesadas?|computadas?)\s*[:\(]?\s*([\d,\.]+)',
            texto, re.I
        )
        if m2:
            actas_proc = _numero(m2.group(1))

        # Para envío al JEE
        m3 = re.search(r'(?:jee|envío al jee|para envío)\s*[:\(]?\s*([\d,\.]+)', texto, re.I)
        if m3:
            actas_jee = _numero(m3.group(1))

        # Porcentaje como fallback para calcular procesadas
        if actas_proc == 0:
            mp = re.search(r'([\d]{1,3}[,\.][\d]{3,4})\s*%', texto)
            if mp:
                pct_f = _pct(mp.group(1))
                t = total or TOTAL_ACTAS_FIJO
                actas_proc = int(pct_f / 100 * t)

    except Exception:
        pass

    return candidatos, actas_proc, actas_jee, total or TOTAL_ACTAS_FIJO


# ── Función principal de scraping ─────────────────────────────────────────────
def obtener_resultados() -> dict:
    if not PLAYWRIGHT_OK:
        return _vacio(
            "Playwright no instalado.\n"
            "Ejecuta:  pip install playwright  &&  playwright install chromium"
        )
    try:
        return _scrape()
    except Exception as e:
        return _vacio(f"Error inesperado: {e}")


def _scrape() -> dict:
    candidatos = []
    actas_proc = 0
    actas_jee  = 0
    total      = TOTAL_ACTAS_FIJO
    error_msg  = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="es-PE",
        )
        pg  = ctx.new_page()
        api = []   # respuestas JSON capturadas

        def on_resp(resp):
            ct  = resp.headers.get("content-type", "")
            url = resp.url.lower()
            if "json" in ct:
                try:
                    data = resp.json()
                    api.append({"url": url, "data": data})
                except Exception:
                    pass

        pg.on("response", on_resp)

        try:
            pg.goto(URL_ONPE, timeout=40000, wait_until="networkidle")
        except Exception:
            try:
                pg.goto(URL_ONPE, timeout=25000, wait_until="domcontentloaded")
                pg.wait_for_timeout(7000)
            except Exception as ex:
                browser.close()
                return _vacio(f"No se pudo cargar ONPE: {ex}")

        # Esperar contenido dinámico
        for selector in ["table", "tbody tr", "[class*='candidat']", "[class*='result']"]:
            try:
                pg.wait_for_selector(selector, timeout=10000)
                break
            except Exception:
                pass
        pg.wait_for_timeout(3000)

        # ── 1) Buscar en APIs capturadas ──
        # Priorizar URLs con palabras clave presidenciales
        api_sorted = sorted(
            api,
            key=lambda x: sum(1 for k in [
                "presidencial", "resumen", "candidato", "resultado", "computo"
            ] if k in x["url"]),
            reverse=True,
        )
        for item in api_sorted:
            c, ap, aj, t = _buscar_en_json(item["data"])
            if c:
                candidatos = c
            if ap:
                actas_proc = ap
            if aj:
                actas_jee = aj
            if t:
                total = t
            if candidatos:
                break

        # ── 2) Si no hubo API, parsear DOM ──
        if not candidatos or actas_proc == 0:
            c_dom, ap_dom, aj_dom, t_dom = _parsear_dom(pg)
            if not candidatos and c_dom:
                candidatos = c_dom
            if not actas_proc and ap_dom:
                actas_proc = ap_dom
            if not actas_jee and aj_dom:
                actas_jee = aj_dom
            if not total or total == TOTAL_ACTAS_FIJO:
                total = t_dom

        browser.close()

    total = total or TOTAL_ACTAS_FIJO

    if not candidatos:
        error_msg = (
            "Sin datos disponibles aún.\n"
            "La ONPE publica resultados progresivamente.\n"
            "La app reintentará automáticamente."
        )

    pct_actas    = round(actas_proc / total * 100, 3) if total > 0 else 0.0
    pct_jee      = round(actas_jee  / total * 100, 3) if total > 0 else 0.0
    pendientes   = max(total - actas_proc - actas_jee, 0)
    pct_pend     = round(pendientes  / total * 100, 3) if total > 0 else 100.0

    return {
        "candidatos":      candidatos,
        "pct_actas":       pct_actas,
        "actas_proc":      actas_proc,
        "actas_jee":       actas_jee,
        "pct_jee":         pct_jee,
        "pendientes":      pendientes,
        "pct_pend":        pct_pend,
        "total":           total,
        "hora":            datetime.now().strftime("%d/%m/%Y A LAS %I:%M:%S %p").upper(),
        "error":           error_msg,
    }


def _vacio(error: str) -> dict:
    return {
        "candidatos": [], "pct_actas": 0.0,
        "actas_proc": 0, "actas_jee": 0,
        "pct_jee": 0.0, "pendientes": TOTAL_ACTAS_FIJO,
        "pct_pend": 100.0, "total": TOTAL_ACTAS_FIJO,
        "hora": datetime.now().strftime("%d/%m/%Y A LAS %I:%M:%S %p").upper(),
        "error": error,
    }


# ═══════════════════════════════════════════════════════════
#  INTERFAZ FLET
# ═══════════════════════════════════════════════════════════

def main(page: ft.Page):
    page.title   = "Elecciones Perú 2026 — Resultados ONPE"
    page.bgcolor = "#070E1A"
    page.padding = 0
    page.scroll  = ft.ScrollMode.AUTO
    page.window_width  = 1120
    page.window_height = 840

    _estado = {"corriendo": True}

    # ── Tarjeta candidato ─────────────────────────────────
    def tarjeta(pos, nombre, partido, votos, pct, color):
        barra  = max(min(pct, 100), 0.5)
        es_top = pos <= 3
        return ft.Container(
            expand=True,
            margin=ft.Margin(left=4, right=4, top=4, bottom=4),
            padding=ft.Padding(left=11, right=11, top=10, bottom=10),
            bgcolor="#0A2847" if es_top else "#0C1E33",
            border_radius=10,
            border=ft.Border.all(2 if es_top else 1, color if es_top else "#1A3050"),
            content=ft.Column(
                spacing=5,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            # Número posición
                            ft.Container(
                                width=26, height=26, border_radius=13,
                                bgcolor=color, alignment=ft.Alignment.CENTER,
                                content=ft.Text(
                                    str(pos), color="white",
                                    size=11, weight=ft.FontWeight.BOLD,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ),
                            # Nombre + partido
                            ft.Column(
                                spacing=1, expand=True,
                                controls=[
                                    ft.Text(
                                        nombre,
                                        color="white",
                                        size=11,
                                        weight=ft.FontWeight.BOLD if es_top else ft.FontWeight.W_500,
                                        max_lines=2,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    ft.Text(
                                        partido,
                                        color="#90CAF9", size=9,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                        visible=bool(partido),
                                    ),
                                ],
                            ),
                            # Porcentaje
                            ft.Text(
                                f"{pct:.2f}%",
                                color=color,
                                size=18 if es_top else 14,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                    ),
                    # Votos
                    ft.Text(
                        f"🗳  {votos:,} votos" if votos > 0 else "🗳  — votos",
                        color="#78909C", size=10,
                    ),
                    # Barra
                    ft.Row(
                        spacing=0,
                        controls=[
                            ft.Container(
                                height=4, border_radius=2, bgcolor=color,
                                expand=int(barra * 10),
                            ),
                            ft.Container(
                                height=4, border_radius=2, bgcolor="#162D44",
                                expand=int((100 - barra) * 10),
                            ),
                        ],
                    ),
                ],
            ),
        )

    # ── Widgets de estado ────────────────────────────────
    txt_pct_grande    = ft.Text("", color="#42A5F5", size=15, weight=ft.FontWeight.BOLD)
    txt_total_actas   = ft.Text("", color="#B0BEC5", size=12)
    barra_actas       = ft.ProgressBar(value=0, bgcolor="#162D44", color="#1976D2",
                                        height=8, border_radius=4)

    txt_contab        = ft.Text("", color="#A5D6A7", size=12, weight=ft.FontWeight.W_500)
    txt_jee           = ft.Text("", color="#90CAF9", size=12)
    txt_pend          = ft.Text("", color="#EF9A9A", size=12)
    txt_actualizado   = ft.Text("", color="#546E7A", size=11)
    txt_countdown     = ft.Text("", color="#37474F", size=11)

    col1 = ft.Column(spacing=0, expand=True)
    col2 = ft.Column(spacing=0, expand=True)
    col3 = ft.Column(spacing=0, expand=True)
    panel_err = ft.Container(visible=False)
    ring      = ft.ProgressRing(color="#42A5F5", visible=False, width=18, height=18, stroke_width=2)
    btn_ref   = ft.IconButton(
        icon=ft.Icons.REFRESH_ROUNDED, icon_color="#42A5F5",
        icon_size=20, tooltip="Actualizar ahora",
    )

    # ── Mostrar datos ────────────────────────────────────
    def mostrar(d: dict):
        error = d.get("error")
        txt_actualizado.value = f"⏱  ACTUALIZADO {d['hora']}"

        ap   = d["actas_proc"]
        at   = d["total"]
        jee  = d["actas_jee"]
        pend = d["pendientes"]
        pct  = d["pct_actas"]
        pjee = d["pct_jee"]
        ppend= d["pct_pend"]

        txt_pct_grande.value  = f"Actas contabilizadas: {pct:.3f} %"
        txt_total_actas.value = f"Total de actas: {at:,}"
        barra_actas.value     = pct / 100

        txt_contab.value = f"✅  Contabilizadas ({ap:,})"
        txt_jee.value    = f"📤  Para envío al JEE ({jee:,})  ·  {pjee:.3f} %"
        txt_pend.value   = f"⏳  Pendientes ({pend:,})  ·  {ppend:.3f} %"

        if error:
            panel_err.visible = True
            panel_err.content = ft.Container(
                padding=12, border_radius=10,
                bgcolor="#05111F",
                border=ft.Border.all(1, "#1565C0"),
                content=ft.Column(
                    spacing=4,
                    controls=[
                        ft.Row(controls=[
                            ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, color="#42A5F5", size=15),
                            ft.Text("  Estado", color="#90CAF9", size=12,
                                    weight=ft.FontWeight.BOLD),
                        ]),
                        ft.Text(error, color="#78909C", size=11),
                    ],
                ),
            )
            col1.controls.clear()
            col2.controls.clear()
            col3.controls.clear()
        else:
            panel_err.visible = False
            col1.controls.clear()
            col2.controls.clear()
            col3.controls.clear()

            cands = sorted(d["candidatos"], key=lambda c: c["porcentaje"], reverse=True)[:12]
            for i, c in enumerate(cands):
                card = tarjeta(
                    i + 1, c["nombre"], c.get("partido", ""),
                    c["votos"], c["porcentaje"], COLORES[i % len(COLORES)]
                )
                [col1, col2, col3][i % 3].controls.append(card)

            if not cands:
                col1.controls.append(
                    ft.Text("Sin resultados aún — reintentando...", color="#37474F", size=12)
                )
        try:
            page.update()
        except Exception:
            pass

    # ── Ciclo de actualización ───────────────────────────
    def actualizar(e=None):
        ring.visible       = True
        btn_ref.disabled   = True
        txt_countdown.value = "⏳  Consultando ONPE..."
        try:
            page.update()
        except Exception:
            pass
        d = obtener_resultados()
        mostrar(d)
        ring.visible     = False
        btn_ref.disabled = False
        try:
            page.update()
        except Exception:
            pass

    btn_ref.on_click = lambda e: threading.Thread(target=actualizar, daemon=True).start()

    def bucle():
        actualizar()
        while _estado["corriendo"]:
            for i in range(INTERVALO, 0, -1):
                if not _estado["corriendo"]:
                    return
                txt_countdown.value = f"Próxima actualización en {i}s"
                try:
                    page.update()
                except Exception:
                    return
                time.sleep(1)
            if _estado["corriendo"]:
                actualizar()

    # ── Layout ──────────────────────────────────────────
    GRAD = ft.LinearGradient(
        begin=ft.Alignment(-1, -1),
        end=ft.Alignment(1, 1),
        colors=["#050C18", "#091B32"],
    )

    # Panel superior de actas (fondo destacado)
    panel_actas = ft.Container(
        padding=ft.Padding(left=14, right=14, top=10, bottom=10),
        bgcolor="#05111F",
        border_radius=10,
        border=ft.Border.all(1, "#1A3A5C"),
        content=ft.Column(
            spacing=6,
            controls=[
                # Fila: pct grande + total
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[txt_pct_grande, txt_total_actas],
                ),
                barra_actas,
                # 3 stats en fila
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        txt_contab,
                        ft.Container(width=1, bgcolor="#1A3A5C"),
                        txt_jee,
                        ft.Container(width=1, bgcolor="#1A3A5C"),
                        txt_pend,
                    ],
                ),
            ],
        ),
    )

    header = ft.Container(
        padding=ft.Padding(left=18, right=18, top=14, bottom=14),
        gradient=GRAD,
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text("🗳️", size=28),
                                ft.Column(
                                    spacing=1,
                                    controls=[
                                        ft.Text(
                                            "ELECCIONES GENERALES PERÚ 2026",
                                            color="white", size=17,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            "Cómputo presidencial en tiempo real  ·  ONPE oficial",
                                            color="#455A64", size=11,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        ft.Row(
                            spacing=4,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[ring, btn_ref],
                        ),
                    ],
                ),
                ft.Divider(color="#1A3050", height=1),
                panel_actas,
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[txt_actualizado, txt_countdown],
                ),
            ],
        ),
    )

    cuerpo = ft.Container(
        padding=ft.Padding(left=10, right=10, top=8, bottom=10),
        content=ft.Column(
            spacing=8,
            controls=[
                panel_err,
                ft.Row(controls=[
                    ft.Icon(ft.Icons.LEADERBOARD_ROUNDED, color="#42A5F5", size=14),
                    ft.Text(
                        "  CANDIDATOS PRESIDENCIALES — TOP 12",
                        color="#42A5F5", size=11, weight=ft.FontWeight.BOLD,
                    ),
                ]),
                # 3 columnas
                ft.Row(
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    spacing=0,
                    controls=[
                        ft.Column(expand=True, spacing=0, controls=[col1]),
                        ft.Column(expand=True, spacing=0, controls=[col2]),
                        ft.Column(expand=True, spacing=0, controls=[col3]),
                    ],
                ),
                ft.Divider(color="#162D44"),
                ft.Text(
                    f"resultadoelectoral.onpe.gob.pe  ·  actualización automática cada {INTERVALO}s",
                    color="#1A2530", size=10,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        ),
    )

    page.add(ft.Column(
        expand=True, spacing=0,
        controls=[header, cuerpo],
    ))

    threading.Thread(target=bucle, daemon=True).start()
    page.on_close = lambda e: _estado.update({"corriendo": False})


if __name__ == "__main__":
    ft.run(main=main)