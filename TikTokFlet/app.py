"""
╔══════════════════════════════════════════════════════╗
║   CARRERA DE PAÍSES — App de control                ║
║   Requiere: pip install flet fastapi uvicorn        ║
║   Ejecutar:  python app.py                          ║
╚══════════════════════════════════════════════════════╝
"""
import flet as ft
import threading
import webbrowser
import time
import os

from servidor import crear_servidor, broadcast_evento

# ── Ruta del HTML (debe estar en la misma carpeta) ──
HTML_PATH = os.path.join(os.path.dirname(__file__), "carrera_tiktok.html")
HTML_URL  = "http://localhost:3000/carrera"   # lo sirve el servidor


def main(page: ft.Page):
    # ══════════════════════════════════════════
    #  CONFIGURACIÓN DE VENTANA
    # ══════════════════════════════════════════
    page.title        = "🐎 Carrera de Países — Control"
    page.window.width  = 860
    page.window.height = 780
    page.window.min_width  = 800
    page.window.min_height = 600
    page.bgcolor      = "#0a0f1e"
    page.padding      = ft.Padding(0, 0, 0, 0)
    page.theme_mode   = ft.ThemeMode.DARK

    # ══════════════════════════════════════════
    #  ESTADO
    # ══════════════════════════════════════════
    servidor_activo = {"v": False}

    # ══════════════════════════════════════════
    #  HELPERS UI
    # ══════════════════════════════════════════
    def label(texto, size=11, color="#64748b", bold=False):
        return ft.Text(
            texto,
            size=size,
            color=color,
            weight=ft.FontWeight.BOLD if bold else ft.FontWeight.NORMAL,
        )

    def seccion(titulo):
        return ft.Container(
            content=ft.Text(titulo, size=10, color="#38bdf8",
                            weight=ft.FontWeight.BOLD),
            padding=ft.Padding(0, 8, 0, 2),
        )

    def slider_config(etiqueta, minv, maxv, valor, paso, fmt, ref_texto):
        """Slider con etiqueta + valor en tiempo real."""
        def on_change(e):
            ref_texto.current.value = fmt.format(e.control.value)
            page.update()

        sl = ft.Slider(
            min=minv, max=maxv, value=valor, divisions=int((maxv-minv)/paso),
            active_color="#38bdf8",
            thumb_color="#38bdf8",
            on_change=on_change,
            expand=True,
        )
        val_text = ft.Text(fmt.format(valor), size=11, color="#e2e8f0",
                           ref=ref_texto, width=52, text_align=ft.TextAlign.RIGHT)
        return sl, ft.Row([
            label(etiqueta, size=10),
            ft.Container(expand=True),
            val_text,
        ]), sl

    # ══════════════════════════════════════════
    #  LOG DE EVENTOS
    # ══════════════════════════════════════════
    log_list = ft.ListView(
        expand=True,
        spacing=2,
        auto_scroll=True,
    )

    def agregar_log(tipo, msg, color="#94a3b8"):
        icon_map = {"chat": "💬", "gift": "🎁", "like": "❤️",
                    "obs": "🚧", "sys": "⚙️", "error": "❌"}
        icono = icon_map.get(tipo, "•")
        log_list.controls.append(
            ft.Container(
                content=ft.Text(f"{icono}  {msg}", size=10, color=color,
                                no_wrap=False),
                padding=ft.Padding(6, 2, 6, 2),
                border=ft.Border(
                    left=ft.BorderSide(2, color),
                ),
                bgcolor="#0f172a",
                border_radius=4,
            )
        )
        if len(log_list.controls) > 120:
            log_list.controls.pop(0)
        page.update()

    # ══════════════════════════════════════════
    #  SLIDERS — referencias a texto del valor
    # ══════════════════════════════════════════
    ref_vel    = ft.Ref[ft.Text]()
    ref_boost_c = ft.Ref[ft.Text]()
    ref_boost_g = ft.Ref[ft.Text]()
    ref_likes  = ft.Ref[ft.Text]()
    ref_decay  = ft.Ref[ft.Text]()

    sl_vel,     row_vel,     _ = slider_config("Velocidad base",    0.003, 0.05,  0.012, 0.001, "{:.3f}", ref_vel)
    sl_boost_c, row_boost_c, _ = slider_config("Boost comentario",  0.05,  1.0,   0.25,  0.05,  "{:.2f}", ref_boost_c)
    sl_boost_g, row_boost_g, _ = slider_config("Boost donación",    0.5,   5.0,   2.5,   0.1,   "{:.1f}", ref_boost_g)
    sl_likes,   row_likes,   _ = slider_config("Likes → obstáculo", 2,     20,    5,     1,     "{:.0f}", ref_likes)
    sl_decay,   row_decay,   _ = slider_config("Decaimiento boost", 0.80,  0.99,  0.92,  0.01,  "{:.2f}", ref_decay)

    # ── Campo GIF/imagen de fondo ──
    tf_gif = ft.TextField(
        value="https://i.pinimg.com/originals/84/7b/10/847b107ffd33367e0d943d4f4c5fc0ef.gif",
        hint_text="URL de GIF o imagen de fondo",
        text_size=10,
        color="#e2e8f0",
        bgcolor="#0f172a",
        border_color="#334155",
        focused_border_color="#38bdf8",
        cursor_color="#38bdf8",
        height=40,
        expand=True,
    )

    # ── Estado del servidor ──
    status_dot = ft.Container(width=10, height=10, border_radius=5, bgcolor="#ef4444")
    status_txt = ft.Text("Servidor detenido", size=11, color="#ef4444")

    def set_status(activo: bool):
        if activo:
            status_dot.bgcolor = "#4ade80"
            status_txt.value   = "Servidor activo en :3000"
            status_txt.color   = "#4ade80"
        else:
            status_dot.bgcolor = "#ef4444"
            status_txt.value   = "Servidor detenido"
            status_txt.color   = "#ef4444"
        page.update()

    # ══════════════════════════════════════════
    #  BOTONES DE ACCIÓN
    # ══════════════════════════════════════════
    def iniciar_servidor(e):
        if servidor_activo["v"]:
            agregar_log("sys", "El servidor ya está activo.")
            return
        config = get_config()
        threading.Thread(
            target=crear_servidor,
            args=(config, agregar_log),
            daemon=True,
        ).start()
        servidor_activo["v"] = True
        set_status(True)
        agregar_log("sys", "Servidor iniciado en http://localhost:3000", "#4ade80")
        time.sleep(0.8)
        webbrowser.open(HTML_URL)
        agregar_log("sys", "Vista previa abierta en el navegador", "#38bdf8")

    def abrir_preview(e):
        webbrowser.open(HTML_URL)
        agregar_log("sys", "Vista previa abierta en el navegador", "#38bdf8")

    def aplicar_config(e):
        config = get_config()
        broadcast_evento({
            "event":    "__config__",
            "BASE_SPD": config["BASE_SPD"],
            "BOOST_COMMENT": config["BOOST_COMMENT"],
            "BOOST_GIFT":    config["BOOST_GIFT"],
            "LIKES_FOR_OBS": config["LIKES_FOR_OBS"],
            "BOOST_DECAY":   config["BOOST_DECAY"],
            "BG_URL":        config["BG_URL"],
        })
        agregar_log("sys", f"Config aplicada → vel={config['BASE_SPD']:.3f} "
                           f"c={config['BOOST_COMMENT']:.2f} "
                           f"g={config['BOOST_GIFT']:.1f}", "#fbbf24")

    def reiniciar_carrera(e):
        broadcast_evento({"event": "__reset__"})
        agregar_log("sys", "Carrera reiniciada 🔄", "#fbbf24")

    def simular_evento(tipo, idx=0):
        """Simula un evento para probar sin Tikfinity."""
        paises = ["peru","mexico","bolivia","guatemala","ecuador",
                  "argentina","colombia","españa","el salvador","chile",
                  "venezuela","costa rica","nicaragua","paraguay",
                  "honduras","brasil","uruguay"]
        if tipo == "chat":
            broadcast_evento({"event":"chat","comment": paises[idx]})
            agregar_log("chat", f"[TEST] Comentario: {paises[idx]}", "#fbbf24")
        elif tipo == "gift":
            gifts = ["1_1.webp","1_2.webp","1_3.webp","1_4.webp","1_5.webp",
                     "1_6.webp","1_7.webp","1_8.webp","1_9.webp","1_10.webp",
                     "1_11.webp","1_12.webp","1_13.webp","1_14.webp","1_15.webp",
                     "1_16.webp","1_17.webp"]
            broadcast_evento({"event":"gift","giftName": gifts[idx]})
            agregar_log("gift", f"[TEST] Regalo: {gifts[idx]}", "#f472b6")
        elif tipo == "like":
            broadcast_evento({"event":"like","likeCount":"5"})
            agregar_log("like", "[TEST] 5 likes → obstáculo", "#fb7185")
        elif tipo == "obs":
            broadcast_evento({"event":"__obstacle__","idx": idx})
            agregar_log("obs", f"[TEST] Obstáculo → país #{idx+1}", "#ef4444")

    # País selector para pruebas
    dd_pais = ft.Dropdown(
        options=[ft.dropdown.Option(str(i), p) for i, p in enumerate([
            "🇵🇪 Perú","🇲🇽 México","🇧🇴 Bolivia","🇬🇹 Guatemala","🇪🇨 Ecuador",
            "🇦🇷 Argentina","🇨🇴 Colombia","🇪🇸 España","🇸🇻 El Salvador","🇨🇱 Chile",
            "🇻🇪 Venezuela","🇨🇷 Costa Rica","🇳🇮 Nicaragua","🇵🇾 Paraguay",
            "🇭🇳 Honduras","🇧🇷 Brasil","🇺🇾 Uruguay",
        ])],
        value="0",
        text_size=11,
        bgcolor="#0f172a",
        border_color="#334155",
        focused_border_color="#38bdf8",
        height=40,
        expand=True,
    )

    def get_config():
        return {
            "BASE_SPD":      sl_vel.value,
            "BOOST_COMMENT": sl_boost_c.value,
            "BOOST_GIFT":    sl_boost_g.value,
            "LIKES_FOR_OBS": int(sl_likes.value),
            "BOOST_DECAY":   sl_decay.value,
            "BG_URL":        tf_gif.value.strip(),
        }

    def btn(texto, icono, color_bg, on_click, expand=False):
        return ft.ElevatedButton(
            content=ft.Row(
                [ft.Icon(icono, size=14, color="#fff"),
                 ft.Text(texto, size=11, color="#fff", weight=ft.FontWeight.BOLD)],
                spacing=6,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor=color_bg,
            on_click=on_click,
            expand=expand,
            height=36,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
                overlay_color=ft.Colors.WHITE24,
            ),
        )

    # ══════════════════════════════════════════
    #  LAYOUT — PANEL IZQUIERDO
    # ══════════════════════════════════════════
    panel_config = ft.Container(
        width=340,
        bgcolor="#0f172a",
        border=ft.Border(right=ft.BorderSide(1, "#1e293b")),
        padding=ft.Padding(14, 14, 14, 10),
        content=ft.Column(
            spacing=4,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            controls=[
                # Estado servidor
                ft.Container(
                    content=ft.Row(
                        [status_dot, ft.Container(width=6), status_txt],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor="#1e293b",
                    border_radius=6,
                    padding=ft.Padding(10, 6, 10, 6),
                ),
                ft.Divider(height=8, color="transparent"),

                # Botones principales
                ft.Row([
                    btn("Iniciar servidor", ft.Icons.PLAY_ARROW,
                        "#16a34a", iniciar_servidor, expand=True),
                    btn("Preview", ft.Icons.OPEN_IN_BROWSER,
                        "#0369a1", abrir_preview),
                ], spacing=6),
                ft.Row([
                    btn("Aplicar config", ft.Icons.TUNE,
                        "#7c3aed", aplicar_config, expand=True),
                    btn("Reiniciar", ft.Icons.REFRESH,
                        "#b45309", reiniciar_carrera),
                ], spacing=6),

                ft.Divider(height=6, color="#1e293b"),
                seccion("⚙️  VELOCIDAD Y FÍSICA"),
                row_vel, sl_vel,
                row_boost_c, sl_boost_c,
                row_boost_g, sl_boost_g,
                row_likes, sl_likes,
                row_decay, sl_decay,

                ft.Divider(height=6, color="#1e293b"),
                seccion("🎨  FONDO (GIF o imagen)"),
                ft.Row([tf_gif], spacing=0),

                ft.Divider(height=6, color="#1e293b"),
                seccion("🧪  SIMULAR EVENTOS (pruebas)"),
                ft.Row([dd_pais], spacing=0),
                ft.Row([
                    btn("Comentario", ft.Icons.CHAT_BUBBLE_OUTLINE,
                        "#0369a1",
                        lambda e: simular_evento("chat", int(dd_pais.value)),
                        expand=True),
                    btn("Donación", ft.Icons.CARD_GIFTCARD,
                        "#7c3aed",
                        lambda e: simular_evento("gift", int(dd_pais.value)),
                        expand=True),
                ], spacing=6),
                ft.Row([
                    btn("5 Likes", ft.Icons.FAVORITE,
                        "#be123c",
                        lambda e: simular_evento("like"),
                        expand=True),
                    btn("Obstáculo", ft.Icons.WARNING_AMBER_ROUNDED,
                        "#b45309",
                        lambda e: simular_evento("obs", int(dd_pais.value)),
                        expand=True),
                ], spacing=6),

                ft.Divider(height=6, color="#1e293b"),
                seccion("📋  LOG DE EVENTOS"),
                ft.Container(
                    content=log_list,
                    height=200,
                    bgcolor="#020812",
                    border_radius=6,
                    border=ft.Border.all(1, "#1e293b"),
                    padding=ft.Padding(4, 4, 4, 4),
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                ),
            ],
        ),
    )

    # ══════════════════════════════════════════
    #  LAYOUT — PANEL DERECHO (preview browser)
    # ══════════════════════════════════════════
    panel_preview = ft.Container(
        expand=True,
        bgcolor="#020812",
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            controls=[
                ft.Icon(ft.Icons.SPORTS_SCORE, size=56, color="#1e293b"),
                ft.Text("Vista Previa", size=18, color="#334155",
                        weight=ft.FontWeight.BOLD),
                ft.Text(
                    "El preview se abre en tu navegador\n"
                    "para máxima compatibilidad con\n"
                    "animaciones GIF y CSS del juego.",
                    size=12, color="#475569",
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=8),
                btn("Abrir Preview en Navegador",
                    ft.Icons.OPEN_IN_BROWSER, "#0369a1", abrir_preview),
                ft.Container(height=4),
                ft.Text(
                    "http://localhost:3000/carrera",
                    size=10, color="#334155",
                    font_family="monospace",
                ),
                ft.Container(height=20),
                # Instrucciones rápidas
                ft.Container(
                    content=ft.Column(
                        spacing=6,
                        controls=[
                            _info_row("💬", "Comentario", "Letra del país (A, S, D...)"),
                            _info_row("🎁", "Donación", "Shift + Letra"),
                            _info_row("🚧", "Obstáculo", "Ctrl + Letra"),
                            _info_row("❤️", "Like x5", "Tecla 0"),
                            _info_row("🔄", "Reiniciar", "Tecla R"),
                        ],
                    ),
                    bgcolor="#0f172a",
                    border_radius=10,
                    border=ft.Border.all(1, "#1e293b"),
                    padding=ft.Padding(16, 12, 16, 12),
                    width=280,
                ),
            ],
        ),
    )

    # ══════════════════════════════════════════
    #  ROOT LAYOUT
    # ══════════════════════════════════════════
    page.add(
        ft.Row(
            expand=True,
            spacing=0,
            controls=[panel_config, panel_preview],
        )
    )

    # Auto-iniciar servidor al abrir la app
    iniciar_servidor(None)


def _info_row(icono, titulo, subtitulo):
    return ft.Row(
        spacing=10,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text(icono, size=16),
            ft.Column(spacing=0, controls=[
                ft.Text(titulo, size=11, color="#e2e8f0",
                        weight=ft.FontWeight.BOLD),
                ft.Text(subtitulo, size=10, color="#64748b"),
            ]),
        ],
    )


if __name__ == "__main__":
    ft.run(main, view=ft.AppView.FLET_APP)
