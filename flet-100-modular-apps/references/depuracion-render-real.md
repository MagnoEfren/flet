# Renderizar y depurar una app Flet 1.0 real (Linux, sin monitor)

Usar cuando una pantalla sale gris o vacía, o un cambio visual no se ve,
y las pruebas con `FakePage` pasan sin errores. Esas pruebas no ejecutan
Flutter, así que no pueden detectar errores de dibujo.

## Contenido
1. Preparar el entorno
2. Ver los errores del cliente
3. Arnés que recorre la app y toma capturas
4. Bisección de una vista
5. Trampas del propio arnés

## 1. Preparar el entorno

```bash
# Si apt falla por un repositorio de terceros roto (p. ej. nodesource), quitarlo:
rm -f /etc/apt/sources.list.d/nodesource*
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq xvfb libgtk-3-0 \
    libgstreamer1.0-0 libgstreamer-plugins-base1.0-0 libmpv2 imagemagick
pip install flet-desktop==1.0.0 --break-system-packages

# Pantalla virtual (relanzarla si el proceso se cerró)
export DISPLAY=:99
pgrep Xvfb >/dev/null || (nohup Xvfb :99 -screen 0 1600x1000x24 >/dev/null 2>&1 &)
```

La primera ejecución descarga el cliente de escritorio desde GitHub
("Preparing Flet v1.0.0 for the first use"). Puede tardar un minuto.
Los avisos `libEGL ... DRI3`, `Atk-CRITICAL` y `Timed out waiting for
OpenGL frame` son normales en Xvfb y no indican fallos de la app.

## 2. Ver los errores del cliente

```python
def main(page: ft.Page):
    page.on_error = lambda e: print("ERROR CLIENTE:", e.data, flush=True)
    ...
```

Flutter devuelve aquí el mensaje exacto. Por ejemplo, así se encontró
`"colors" must have length 2 if "colorStops" is omitted`, que hacía
desaparecer el contenido de un `Canvas`.

## 3. Arnés que recorre la app y toma capturas

```python
import os, sys, time, subprocess
sys.path.insert(0, "/ruta/al/proyecto"); os.chdir("/ruta/al/proyecto")
import flet as ft
import main as M          # el main.py de la app
import config

def shot(nombre):
    subprocess.run(["import", "-window", "root", f"/tmp/shots/{nombre}.png"])

def recorrer(app):
    page = app.page
    time.sleep(5); shot("0_inicio")
    # Simular clics SIEMPRE en el bucle de la página (ver sección 5):
    page.run_task(app.wizard._next, None).result(timeout=10)   # handler async
    time.sleep(2); shot("1_paso")

    async def ir(clave):                                        # métodos síncronos: envolver
        app.on_nav(clave)
    page.run_task(ir, "ajustes").result(timeout=10)
    time.sleep(2); shot("2_ajustes")

def run(page: ft.Page):
    page.on_error = lambda e: print("ERROR CLIENTE:", e.data, flush=True)
    app = M.App(page)
    page.window.width, page.window.height = 1280, 800
    page.update()
    page.run_thread(recorrer, app)

os.makedirs("/tmp/shots", exist_ok=True)
ft.run(run, assets_dir=str(config.ASSETS_DIR))
```

```bash
timeout 90 python3 arnes.py > /tmp/arnes.log 2>&1
grep -v "libEGL\|Atk\|OpenGL\|^$" /tmp/arnes.log          # errores reales
# Recortar al tamaño de la ventana y reducir para revisar varias juntas
for f in /tmp/shots/*.png; do convert "$f" -crop 1280x800+0+0 +repage -resize 50% "${f%.png}_s.png"; done
convert /tmp/shots/0_inicio_s.png /tmp/shots/1_paso_s.png +append /tmp/shots/combo.png
```

Revisar cada pantalla en modo claro **y** oscuro.

## 4. Bisección de una vista

Si una vista sale gris, renderizarla sola y ocultar partes con
`visible=False` hasta encontrar la pieza culpable:

```python
def run(page: ft.Page):
    page.on_error = lambda e: print("ERROR CLIENTE:", e.data, flush=True)
    vista = MiVista(contexto_falso)          # la vista sospechosa, aislada
    parte = os.environ.get("PARTE", "todo")
    if parte == "izq":
        vista.content.controls[1].visible = False
    if parte == "der":
        vista.content.controls[0].visible = False
    page.add(ft.Container(content=vista, height=560))
    page.add(ft.Text("FIN-DEL-ARBOL", color="#FF0000"))  # si se ve, el árbol se dibujó hasta aquí
```

Pista clave: si la vista sigue gris **aunque se oculte todo su
contenido**, el problema está en el propio contenedor de la vista, no en
sus hijos. Revisar atributos que chocan con propiedades de Flet
(`self.left`, `self.width`, …): ver el detector de la sección 19 de SKILL.md.

## 5. Trampas del propio arnés

- **Clics simulados desde otro hilo**: llamar `asyncio.run(handler(e))`
  o un método síncrono directamente desde el hilo del arnés cambia el
  estado (el paso avanza), pero la pantalla puede no refrescarse. Eso
  parece un fallo de la app y no lo es. Usar siempre
  `page.run_task(handler, e).result(timeout=10)`.
- **No llamar al script `bisect.py`** (ni con otros nombres de la
  biblioteca estándar): tapa el módulo `bisect`, Flet falla al importar
  y el error confunde.
- Las pruebas con `FakePage` y la serialización del árbol
  (`ObjectPatch.from_diff` + msgpack) siguen siendo útiles para la
  lógica y los tipos de propiedades, pero no reemplazan esta prueba visual.
