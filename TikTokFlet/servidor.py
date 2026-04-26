"""
servidor.py — Servidor HTTP
  • Recibe webhooks de Tikfinity en POST /eventos
  • Retransmite eventos por SSE a todos los clientes
  • Sirve el HTML en GET /carrera
  • Página de diagnóstico en GET /
"""
import http.server
import threading
import urllib.parse
import json
import os
import time

# ── Clientes SSE conectados ──
_clientes: list = []
_clientes_lock  = threading.Lock()

# ── Configuración actual (se puede actualizar desde la app) ──
_config: dict = {}

# ── Callback de log (se inyecta desde app.py) ──
_log_fn = None


def broadcast_evento(data: dict):
    """Envía un evento JSON a todos los clientes SSE conectados."""
    msg = f"data: {json.dumps(data)}\n\n".encode()
    with _clientes_lock:
        muertos = []
        for c in _clientes:
            try:
                c.wfile.write(msg)
                c.wfile.flush()
            except Exception:
                muertos.append(c)
        for c in muertos:
            _clientes.remove(c)


def _log(tipo, msg, color="#94a3b8"):
    if _log_fn:
        _log_fn(tipo, msg, color)
    else:
        print(f"[{tipo}] {msg}")


def _traducir_tikfinity(data: dict) -> dict:
    """
    Convierte el formato de Tikfinity (triggerTypeId) al formato
    que entiende el HTML (event: chat|gift|like).
    """
    tid = str(data.get("triggerTypeId", ""))
    out = dict(data)

    if tid == "7":
        out["event"]     = "like"
        out["likeCount"] = data.get("likeCount", "1")
        _log("like", f"❤️  LIKE x{out['likeCount']} de @{data.get('nickname','?')}", "#fb7185")

    elif tid == "11":
        comment = (data.get("commandParams") or
                   data.get("content") or
                   data.get("value2") or "").lower().strip()
        out["event"]   = "chat"
        out["comment"] = comment
        _log("chat", f"💬 '{comment}' de @{data.get('nickname','?')}", "#fbbf24")

    elif tid == "3":
        gift = (data.get("giftName") or
                data.get("content") or
                data.get("value2") or "")
        out["event"]    = "gift"
        out["giftName"] = gift
        _log("gift", f"🎁 Regalo '{gift}' de @{data.get('nickname','?')}", "#f472b6")

    else:
        _log("sys", f"Tipo desconocido triggerTypeId={tid}", "#64748b")

    return out


class _Handler(http.server.BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass  # silenciar logs HTTP en consola

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    # ── GET ──────────────────────────────────
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path

        # ── SSE stream ──
        if path == "/stream":
            self.send_response(200)
            self.send_header("Content-Type",  "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection",    "keep-alive")
            self._cors()
            self.end_headers()
            # Registro
            with _clientes_lock:
                _clientes.append(self)
            # Mandar ping inicial
            try:
                self.wfile.write(b'data: {"type":"connected"}\n\n')
                self.wfile.flush()
            except Exception:
                pass
            # Mantener conexión viva
            try:
                while True:
                    time.sleep(15)
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
            except Exception:
                pass
            finally:
                with _clientes_lock:
                    if self in _clientes:
                        _clientes.remove(self)
            return

        # ── Sirve el HTML del juego ──
        if path in ("/carrera", "/carrera/"):
            html_path = os.path.join(os.path.dirname(__file__), "carrera_tiktok.html")
            if not os.path.exists(html_path):
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"carrera_tiktok.html no encontrado")
                return
            with open(html_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self._cors()
            self.end_headers()
            self.wfile.write(content)
            return

        # ── Página de diagnóstico ──
        if path in ("/", ""):
            html = _pagina_diagnostico()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self._cors()
            self.end_headers()
            self.wfile.write(html.encode())
            return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Not found")

    # ── POST ─────────────────────────────────
    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path

        if path != "/eventos":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length).decode("utf-8", errors="replace")

        # Parsear JSON o form-urlencoded
        data = {}
        try:
            data = json.loads(body)
        except Exception:
            try:
                params = urllib.parse.parse_qs(body, keep_blank_values=True)
                data   = {k: v[0] for k, v in params.items()}
            except Exception:
                pass

        # Traducir y retransmitir
        translated = _traducir_tikfinity(data)
        broadcast_evento(translated)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.end_headers()
        self.wfile.write(b'{"ok":true}')


def _pagina_diagnostico() -> str:
    return """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Servidor Carrera</title>
<style>
  body{font-family:monospace;background:#0f172a;color:#e2e8f0;padding:20px;}
  h2{color:#38bdf8;} .ok{color:#4ade80;} .warn{color:#facc15;}
  #log{background:#020812;padding:12px;border-radius:8px;height:360px;
       overflow-y:auto;font-size:12px;}
  .ev{border-left:3px solid #38bdf8;padding:3px 10px;margin:3px 0;background:#0f172a;}
  a{color:#38bdf8;}
</style></head>
<body>
<h2>🐎 Servidor Carrera — Diagnóstico</h2>
<p class="ok">✅ Servidor activo en puerto 3000</p>
<p class="warn">Tikfinity → POST <b>http://localhost:3000/eventos</b></p>
<p>Juego → <a href="/carrera" target="_blank">http://localhost:3000/carrera</a></p>
<div id="log"><em style="color:#475569">Esperando eventos...</em></div>
<script>
const es=new EventSource("/stream"),log=document.getElementById("log");
es.onmessage=e=>{
  const d=JSON.parse(e.data);
  if(d.type==="connected")return;
  const div=document.createElement("div");
  div.className="ev";
  div.textContent=new Date().toLocaleTimeString()+" → "+JSON.stringify(d);
  log.insertBefore(div,log.firstChild);
};
</script></body></html>"""


def crear_servidor(config: dict, log_fn=None):
    """
    Inicia el servidor HTTP en el hilo actual (llamar en un thread daemon).
    config: dict con BASE_SPD, BOOST_COMMENT, etc.
    log_fn: función (tipo, msg, color) para mostrar logs en la UI Flet.
    """
    global _config, _log_fn
    _config = config
    _log_fn = log_fn

    server = http.server.ThreadingHTTPServer(("", 3000), _Handler)
    _log("sys", "Servidor HTTP listo en http://localhost:3000", "#4ade80")
    server.serve_forever()
