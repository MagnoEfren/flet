---
name: "flet-100-modular-apps"
description: Construir apps móviles/desktop/web en Python con Flet 1.0.0, usando arquitectura modular profesional (theme/database/models/services/components/views) y las convenciones de API correctas de esta versión (que difieren de las versiones de Flet anteriores a 1.0.0 y de casi todo el código de ejemplo viejo en internet, incluido el conocimiento "por defecto" de un LLM). Usar SIEMPRE que el usuario pida crear, corregir, migrar o extender una app en Flet, o mencione ft.run, ft.app, "Flet 1.0", ElevatedButton, FilePicker, Canvas, Dropdown, errores de compilación con flet build, o síntomas como "la pantalla sale gris", "no aparece el texto", "un contenedor sale vacío" o "la vista no cambia", aunque no nombre Flet en ese mensaje.
---

# Flet 1.0.0 — Apps modulares

Referencia acumulada y verificada contra el changelog oficial de
**Flet 1.0.0** (release estable, primera versión mayor tras la serie
0.8x/0.9x). Esta es una versión con **breaking changes reales**: mucho
código de ejemplo en internet, tutoriales viejos, código generado por
un LLM con conocimiento desactualizado, e incluso proyectos propios
escritos para Flet 0.85.x **ya no funcionan tal cual**. Esta guía
documenta exclusivamente lo que es correcto **hoy, en 1.0.0** — no
mezclar con convenciones de versiones anteriores.

## Versión objetivo

Todo el código debe apuntar a `flet==1.0.0` (y `flet-charts==1.0.0` si
se usan gráficos, `flet-local-auth==1.0.0` si se usa autenticación
biométrica) salvo que el usuario pida explícitamente otra versión.

## Verificar la API con `scripts/fletapi.py` (flet-mcp 1.0.0), gastando poco

El script usa el índice oficial de **`flet-mcp==1.0.0`** (la versión
de flet-mcp debe coincidir con la de Flet; se instala sola la primera
vez). No requiere tener `flet` instalado ni configurar un servidor MCP.
Ruta: `scripts/fletapi.py` dentro de esta skill (`SKILL_DIR` = la
carpeta donde está este SKILL.md).

Reglas para no desperdiciar tokens:
- **No consultar lo que esta guía ya cubre** (secciones 0–21). Consultar
  solo controles, parámetros, enums o íconos que no aparecen aquí o de
  los que haya duda real.
- **Agrupar** todas las dudas en **una sola** llamada `q`, nunca una por una.
- No leer el código del script ni pedir su ayuda: el uso está aquí abajo.
- Al terminar de escribir código, correr **una vez** `check` sobre el
  proyecto: solo imprime los problemas (o una línea "OK"). Corregir y
  volver a correrlo solo si hubo problemas.

```bash
# Varias dudas en una sola llamada:
python3 SKILL_DIR/scripts/fletapi.py q Chip SegmentedButton.on_change Icons.AGRICULTURE icon:farm
#   X            -> props, eventos, métodos (* = async) y heredados de X
#   X.miembro    -> doc completa del miembro (encuentra heredados)
#   Enum.MIEMBRO -> "existe" o similares
#   icon:palabra -> íconos por concepto (en inglés)
#   ex:texto / exget:ID -> ejemplos oficiales   ·   cli:build -> opciones de la CLI

# Revisión final del proyecto (ft.X inexistentes, Enum.MIEMBRO, kwargs inválidos):
python3 SKILL_DIR/scripts/fletapi.py check NombreApp/
```

Límites conocidos (no son errores de tu código): el índice no tiene las
propiedades de los tipos de datos (`BorderSide`, `TextStyle`,
`OutlineInputBorder`…) ni el paquete `flet-local-auth`; `check` no los
valida y lo avisa. Para esos casos, si `flet` está instalado, usar
`inspect.signature(ft.X.__init__)`.

## 0. Punto de entrada — `ft.run(main)`, únicamente

```python
import flet as ft

def main(page: ft.Page):
    ...

ft.run(main)
```

En Flet 1.0.0, `ft.app(...)` y `ft.app_async(...)` **ya no existen**
(fueron eliminados; estaban deprecados desde 0.80.0). Tampoco existe
el parámetro `target=` de `run()`/`run_async()` — el primer argumento
posicional es siempre la función de entrada (`main`). Si aparece
`ft.app(target=main)` o `ft.run(target=main)` en código existente
(propio o del usuario), es código para una versión vieja: corregirlo
a `ft.run(main)` como parte del arreglo, incluso si no fue lo que se
pidió explícitamente.

## Arquitectura modular estándar

```
NombreApp/
├── main.py                # Router/orquestador: clase con ir_a(), header/nav dinámicos, layout responsivo
├── pyproject.toml          # Config de build (icons, splash, signing) + deps fijadas con ==
├── theme.py                # Paleta de colores y constantes visuales — un solo lugar
├── assets/                 # icon.png (full-bleed), imágenes de fondo, fuentes (.ttf)
├── database/
│   └── db.py                # SQLite con sqlite3 puro (sin ORM), funciones simples
├── models/
│   └── app_state.py          # Estado compartido: singleton (_instancia = None / __new__)
├── services/                # Lógica de negocio PURA (sin ft.*), testeable con python3 -c "..."
│   └── *_service.py
├── components/              # Piezas de UI reutilizables (funciones que devuelven ft.Control)
└── views/                   # Una vista por pantalla, con método refrescar()
```

- **AppState**: patrón singleton (`_instancia = None`, `__new__`) para compartir datos entre vistas sin pasarlos por props.
- **Vistas**: heredan de `ft.Container` (o de `LayoutControl` si se construye un control propio de bajo nivel, ver sección 8); el contenido pesado se construye en `refrescar()` (no en `__init__`) si depende de datos que cambian; `main.py` llama `vista.refrescar()` antes de mostrarla si el método existe (`hasattr(vista, "refrescar")`).
- **Navegación**: usar `page.push_route(ruta)` (ver sección 9) en vez de manipular vistas a mano cuando la app tiene rutas con URL; para navegación simple entre vistas internas sin URL, seguir usando el router propio (`ir_a()`).
- **Responsivo**: centrar el contenido con un ancho máximo (`MAX_CONTENT_WIDTH`) y reconstruir el layout en `page.on_resize` **solo al cruzar un punto de quiebre** (no en cada píxel). En apps de escritorio que deben verse "sin scroll", repartir el alto con `expand` en `Row`/`Column` (no con alturas fijas) y dejar el desplazamiento solo a las listas (`ft.ListView(expand=True)`).
- **Medidas configurables**: espaciado, padding, radios y duraciones de animación como constantes en `config.py`/`theme.py`, nunca números sueltos repetidos por las vistas.
- **Persistencia antes de salir**: ver sección 12 — no confiar en `atexit`/`__del__` para guardar datos críticos; guardar en el momento en que el dato cambia (o en el handler de cierre) en vez de al terminar el proceso.
- **Testear sin abrir la app**: construir la vista/app con una clase `FakePage` simple y monkeypatchear `BaseControl.update = lambda self: None` y `BaseControl.page = property(lambda self: fake_page)` — así se puede probar toda la lógica por consola antes de que el usuario la corra. **Limitación importante**: esto (y también serializar el árbol de controles) NO detecta errores de dibujo de Flutter. Una app que pasa estas pruebas puede verse gris o vacía en la ventana real. Para cambios visuales, renderizar de verdad (sección 20 y `references/depuracion-render-real.md`).

## Convenciones de API que SIEMPRE debes usar

### 1. Client Actions (`action=`) — la forma preferida para operar con el navegador/OS

Los navegadores (especialmente Safari/iOS) solo permiten abrir un
file picker, escribir al portapapeles, mostrar el share sheet o abrir
una pestaña nueva **mientras siguen procesando el click/tecla del
usuario**. Mandar ese click a Python y esperar la respuesta tarda más
que ese permiso — en iOS Safari esto hacía que `FilePicker.pick_files()`,
`Clipboard.set()`/`set_image()` y `Share` no hicieran nada, sin error
visible (Android y desktop sí dejaban pasar la llamada, por eso
parecía un bug intermitente).

Desde 1.0.0, `Button`, `Container`, `IconButton`, `ListTile`,
`CupertinoButton`, `CupertinoListTile`, `FloatingActionButton`,
`OutlinedButton`, `TextButton` y `TextSpan` aceptan un parámetro
`action` (un `ClientAction` o una lista de ellos) que el cliente
ejecuta **dentro del gesto original**, antes incluso de notificar tu
handler `on_click`:

```python
# Abrir URL — reemplaza el viejo patrón de abrir con url_launcher a mano
ft.Button(content=ft.Text("Abrir sitio"),
          action=ft.OpenUrl("https://flet.dev", target=ft.UrlTarget.BLANK))

# Seleccionar archivo de forma gesture-safe (crítico para web + iOS)
ft.Button(content=ft.Text("Elegir imagen"),
          action=ft.PickFiles(allowed_extensions=["png", "jpg"]),
          on_click=self._al_elegir)  # opcional, se llama después de la acción

# Copiar al portapapeles
ft.IconButton(icon=ft.Icons.COPY, action=ft.CopyToClipboard("texto a copiar"))

# Compartir texto
ft.Button(content=ft.Text("Compartir"), action=ft.ShareText("Mira esto"))
```

Importante: como la acción corre **antes** de que tu código vea el
click, sus argumentos deben conocerse de antemano — para actuar sobre
un valor calculado en el momento del click, setealo en el control
*antes* del click (por ejemplo actualizando `action=ft.CopyToClipboard(valor_actual)`
cuando `valor_actual` cambia, no dentro del handler).

Para `FilePicker` específicamente, además del flujo `action=ft.PickFiles(...)`,
ahora existe el evento `on_result`, que se dispara cuando el usuario
elige archivos vía una acción `PickFiles` (la selección no puede
devolverse como en `pick_files()` porque el diálogo se abrió del lado
del cliente antes de que tu código viera el click):

```python
fp = ft.FilePicker(on_result=self._al_seleccionar)
btn = ft.Button(content=ft.Text("Subir"), action=ft.PickFiles())
# fp y btn deben coexistir en la página (fp no se agrega a overlay, ver sección 2)
```

Para apps de **escritorio nativo** (no servidas como web) esta
limitación de gesto del navegador no aplica, pero usar `action=`
sigue siendo la forma recomendada y más simple.

### 2. Servicios (FilePicker, Share, StoragePaths, Clipboard, UrlLauncher, SharedPreferences, BrowserContextMenu)

Son `Service`, no controles visuales, y se **auto-registran** al
crearse dentro de un handler `async`. Ya **no existen** los accesos
directos `page.clipboard`, `page.url_launcher`, `page.shared_preferences`,
`page.browser_context_menu` ni `page.storage_paths` (fueron eliminados
en 1.0.0, estaban deprecados desde 0.80.0) — instanciar la clase de
servicio directamente:

```python
async def _seleccionar_archivo(self, e):
    fp = ft.FilePicker()
    archivos = await fp.pick_files(
        dialog_title="Selecciona un archivo",
        file_type=ft.FilePickerFileType.CUSTOM,   # o IMAGE, ANY
        allowed_extensions=["xlsx"],
        allow_multiple=False,
    )
    if not archivos:
        return  # el usuario canceló o (en iOS web) el navegador bloqueó el diálogo:
                 # preferir action=ft.PickFiles(...) para ese caso (ver sección 1)
    ruta = archivos[0].path

async def _guardar_como(self, e):
    fp = ft.FilePicker()
    ruta = await fp.save_file(dialog_title="Guardar", file_name="reporte.pdf",
                              file_type=ft.FilePickerFileType.CUSTOM,
                              allowed_extensions=["pdf"])
    # save_file() dispara una descarga en web (no gated por gesto) y sigue
    # funcionando bien en desktop. En Android nativo (flet build apk) puede
    # seguir siendo poco confiable: preferir ft.Share() para "guardar/enviar"
    # en builds Android en vez de un diálogo de guardado.

async def _compartir(self, e):
    await ft.Share().share_files([ft.ShareFile(path=ruta)], title="Compartir")
    # en apps web, considerar ft.ShareText(...) vía action= si se dispara desde un click

async def _carpeta_temporal(self):
    return await ft.StoragePaths().get_temporary_directory()
    # también: get_downloads_directory(), get_application_documents_directory()

async def _copiar(self, texto: str):
    await ft.Clipboard().set(texto)   # en web, preferir action=ft.CopyToClipboard(texto)

async def _abrir_url(self, url: str):
    await ft.UrlLauncher().launch_url(url)   # o preferir action=ft.OpenUrl(url)
```

Reglas que se mantienen igual que en versiones previas:
- Crear una instancia **nueva dentro del handler async** cada vez — nunca guardarlos como `self.file_picker` ni agregarlos a `page.overlay` (eso da error "Unknown control" o timeout).
- Sus métodos son `async` — hay que hacer `await`.

### 3. Handlers async — nunca envueltos en un lambda

Un `lambda` es síncrono aunque llame a una función `async` por dentro
— Flet solo espera (`await`) el handler si detecta que es
`iscoroutinefunction`. Envolver en lambda = la corrutina nunca corre.

```python
# ❌ MAL — nunca se ejecuta de verdad
on_click=lambda e: self._handler_async(e)

# ✅ BIEN — se pasa directo
on_click=self._handler_async
```

Si necesitas pasar datos extra, guárdalos como atributo de instancia
y accédelos dentro del método async (no los pases por parámetro vía lambda).

### 4. NavigationDrawer (menú hamburguesa)

```python
self.drawer = ft.NavigationDrawer(
    bgcolor=theme.CARD_BG,                                    # si no, sale negro por defecto
    indicator_color=ft.Colors.with_opacity(0.12, theme.PRIMARY),
    controls=[...],
    on_change=self._al_elegir_item,     # método async, SIN lambda
)
self.page.drawer = self.drawer

async def _abrir_menu(self, e):
    await self.page.show_drawer()      # async, con await

async def _al_elegir_item(self, e):
    await self.page.close_drawer()     # async, con await
    indice = e.control.selected_index
```

A veces, justo tras recargar la app, el cliente aún no registró el
listener y `show_drawer()`/`close_drawer()` da `TimeoutException`.
Mitigar con un reintento:
```python
async def _abrir_drawer_con_reintento(self):
    try:
        await self.page.show_drawer()
    except Exception:
        await asyncio.sleep(0.3)
        try:
            await self.page.show_drawer()
        except Exception:
            pass
```

### 5. SnackBar y diálogos

`page.show_snack_bar()` **no existe**. `SnackBar` es un `DialogControl`:
```python
def mostrar_snack(control: ft.Control, texto: str, color: str):
    try:
        control.page.show_dialog(
            ft.SnackBar(content=ft.Text(texto, color="#FFFFFF"), bgcolor=color, duration=2600)
        )
    except Exception:
        pass  # el control puede no estar montado todavía

# AlertDialog / diálogos de confirmación:
self.page.show_dialog(ft.AlertDialog(modal=True, title=..., actions=[
    ft.TextButton("Cancelar", on_click=lambda e: self.page.pop_dialog()),
    ft.TextButton("Confirmar", on_click=confirmar),
]))
```

Si las acciones son botones propios (por ejemplo `Container` estilizados),
ponerlos dentro de **una sola** `ft.Row(..., spacing=10, alignment=ft.MainAxisAlignment.END)`
en `actions=[fila]`. Pasados sueltos en la lista salen pegados entre sí.

`ft.use_dialog()` (hook) es seguro de usar en 1.0.0 — el bug de
`IndexError` en el scheduler al renderizar dos veces dentro del mismo
batch fue corregido.

### 6. Dropdown

`DropdownM2` volvió a ser un control soportado (no está deprecado en
1.0.0), así que ambos `ft.Dropdown` y `ft.DropdownM2` son válidos:

```python
self.dd = ft.Dropdown(
    hint_text="Selecciona...",
    hint_style=ft.TextStyle(color=theme.TEXT_PRIMARY),
    options=[ft.DropdownOption(v, style=ft.ButtonStyle(color=theme.TEXT_PRIMARY))
             for v in opciones],          # ft.DropdownOption, NO ft.dropdown.Option
    on_select=self._al_cambiar,           # on_select, NO on_change
    color=theme.TEXT_PRIMARY, text_size=14,
    bgcolor=theme.INPUT_BG,
    border=ft.OutlineInputBorder(side=ft.BorderSide(color="transparent")),  # side=, NO border_side=
    content_padding=ft.Padding.symmetric(horizontal=14, vertical=10),
)
```

Nota sobre bordes: ver sección 10 — `border_color`/`border_width`/
`border_radius` siguen funcionando pero están deprecados a favor de
`border=`.

**Ancho completo**: para que el `Dropdown` ocupe el ancho de su
contenedor usar `expanded_insets=ft.Padding.all(0)`, **no** `expand=True`.
Dentro de una `Column`, `expand` estira el control en **vertical** y deja
un hueco vacío debajo (ver sección 19). Si se le da `width=` fijo, dejar
`expanded_insets=None`.

### 7. Botones — `Button`, no `ElevatedButton`; `content=`, nunca `text=`

`ElevatedButton` fue **eliminado** en 1.0.0 (deprecado desde 0.80.0).
Usar `ft.Button` en su lugar:

```python
ft.Button(content=ft.Text("Guardar"), on_click=...)
ft.OutlinedButton(content=ft.Row(controls=[ft.Icon(...), ft.Text("Editar")]), on_click=...)
# ft.Button(text="Guardar", ...) -> TypeError, siempre usar content=
```

### 8. `ConstrainedControl` fue eliminado — usar `LayoutControl`

Si el usuario (o código heredado) define un control propio heredando
de `ConstrainedControl`, corregirlo a heredar de `LayoutControl`
(deprecado desde 0.80.0, eliminado en 1.0.0).

### 9. Navegación por rutas — `page.push_route()`, no `page.go()`

`Page.go()` fue eliminado. Para navegación basada en URL/rutas usar:
```python
page.push_route("/detalle/123")
```

### 10. `InputBorder` es una jerarquía de clases, no un enum

`InputBorder.OUTLINE` / `.UNDERLINE` / `.NONE` siguen resolviendo por
compatibilidad pero están **deprecados** (se eliminan en 1.3.0) y no
se comportan como enum: `InputBorder.OUTLINE is InputBorder.OUTLINE`
da `False` porque cada acceso crea una instancia nueva — comparar con
`==`, nunca con `is`. Usar las clases directamente:

```python
ft.TextField(
    border=ft.OutlineInputBorder(border_radius=8, side=ft.BorderSide(color=theme.PRIMARY)),
)
# o
ft.TextField(border=ft.UnderlineInputBorder())
# o sin borde:
ft.CupertinoTextField(border=ft.NoInputBorder())
```

Las propiedades sueltas `border_radius`, `border_width`, `border_color`,
`focused_border_width`, `focused_border_color` de `TextField`,
`Dropdown`, `DropdownM2` y `CupertinoTextField` siguen funcionando
pero están deprecadas a favor de `border=` (que acepta un `InputBorder`
o un diccionario `ControlState`); si ambas se setean, `border` gana.
Para código nuevo, preferir siempre `border=`.

El campo de `OutlineInputBorder` es **`side=`** (no `border_side=`, que da
`TypeError`). `TextField` usa **`error=`** para el mensaje de error (no
`error_text=`). Para el borde enfocado, en vez de `focused_border_color`
(deprecado), usar un diccionario por estado:
```python
def borde(color, ancho=1):
    return ft.OutlineInputBorder(border_radius=10, side=ft.BorderSide(width=ancho, color=color))

ft.TextField(border={ft.ControlState.DEFAULT: borde(theme.BORDE),
                     ft.ControlState.FOCUSED: borde(theme.PRIMARY, 1.4),
                     ft.ControlState.ERROR: borde(theme.ERROR)})
```

### 11. `control.page` lanza excepción si no está montado

`if self.content.page:` **no funciona** como "chequeo seguro" — el
`.page` de un control NO montado lanza `RuntimeError`, no devuelve
`None`/`False`. Usar siempre `try/except`:
```python
try:
    self.content.update()
except Exception:
    pass
```

### 12. Cierre de la app y persistencia de datos — sin garantías de limpieza al salir

Desde 1.0.0, un proceso empaquetado (`flet build`) **termina
inmediatamente** al cerrar la ventana o llamar `sys.exit()`, sin
correr el teardown normal del proceso, para evitar un crash real que
ocurría al terminar mientras el hilo de Python seguía vivo dentro de
una extensión C (matplotlib, numpy, Pillow). La consecuencia práctica:
- Los `atexit` handlers, los `__del__` de tus objetos y los buffers de
  escritura sin flush **no tienen garantía de ejecutarse**.
- `SharedPreferences` sí persiste de forma segura en ambos casos.

**Regla de arquitectura**: nunca dejar el guardado de datos críticos
para el cierre de la app (ni en un `atexit`, ni en `__del__`, ni
"guardo todo al final"). Guardar en `services/` inmediatamente después
de cada cambio relevante (ej. al confirmar un formulario, al terminar
una transacción), no de forma diferida.

### 13. Servicio de autenticación biométrica (`flet-local-auth`)

Si el usuario pide login por huella/Face ID, usar la extensión oficial
en vez de implementarlo a mano:
```python
# pyproject.toml: agregar "flet-local-auth==1.0.0" a dependencies
import flet_local_auth as fla

async def _autenticar(self, e):
    ok = await fla.LocalAuthentication().authenticate(
        localized_reason="Confirma tu identidad para continuar"
    )
```
Disponible en Android, iOS, macOS y Windows; **no** en Linux ni Web.

### 14. Gráficos — paquete aparte `flet_charts`

`LineChart`, `BarChart`, `ChartAxis`, etc. **no están en `ft`** —
vienen de `flet-charts` (mismo número de versión que `flet`, ahora `1.0.0`).

```python
import flet_charts as fch

serie = fch.LineChartData(
    points=[...],                 # NO data_points
    rounded_stroke_cap=True,      # NO stroke_cap_round
)
grafico = fch.LineChart(
    data_series=[serie], left_axis=fch.ChartAxis(label_size=34),   # NO labels_size
)
grupo = fch.BarChartGroup(rods=[fch.BarChartRod(bgcolor=..., ...)])  # rods NO bar_rods, bgcolor NO bg_color
grafico_barras = fch.BarChart(groups=[...])                          # groups NO bar_groups
punto = fch.ChartCirclePoint(color="#FF0000")                        # color directo, sin ft.Paint()
```

`pyproject.toml`:
```toml
dependencies = [
    "flet==1.0.0",
    "flet-charts==1.0.0",
    "certifi",              # a veces se pierde en el empaquetado Android si no se declara explícito
]
```

### 15. Imágenes y decoración

```python
ft.Image(src="logo.png", fit=ft.BoxFit.COVER)          # ft.BoxFit, NO ft.ImageFit
ft.Container(
    image=ft.DecorationImage(src="banner.jpg", fit=ft.BoxFit.COVER),
    gradient=ft.LinearGradient(begin=ft.Alignment.TOP_CENTER, end=ft.Alignment.BOTTOM_CENTER,
                               colors=[ft.Colors.with_opacity(0.3, "#000"), ft.Colors.with_opacity(0.8, "#000")]),
    shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.1, "#000"), offset=ft.Offset(0, 2)),
)
```
Usar siempre los alias con guion bajo de `ft.Colors` (`BLACK_12`,
`WHITE_54`, etc.) — los alias sin guion bajo (`BLACK12`, `WHITE10`,
etc.) fueron **eliminados** en 1.0.0.

### 16. Posicionamiento absoluto dentro de un Stack

Los campos `left`/`top`/`right`/`bottom` existen en **cualquier**
control (Row, Column, Container, etc.), no solo en Container — útiles
para decorar con íconos de fondo dentro de un `ft.Stack`.

Consecuencia directa: **nunca** usar esos nombres (ni otros campos de
Flet) como atributos propios en una vista que hereda de `ft.Container`.
Ver sección 19, punto 1.

### 17. `Video` — API simplificada

`Video.show_controls` fue eliminado: usar `Video.controls = None` para
ocultarlos. `Video.playlist_add()`/`playlist_remove()` fueron
eliminados: mutar `Video.playlist` directamente con métodos de lista
(`.append()`, `.pop()`).

### 18. `DragTargetEvent`

`.x`, `.y` y `.offset` fueron eliminados. Usar `.local_position`
(coordenadas relativas al target) o `.global_position` (coordenadas
globales).

### 19. Errores de dibujo: pantalla gris, contenido que desaparece, huecos

Todos estos casos pasan las pruebas con `FakePage` sin ninguna
excepción en Python: el fallo ocurre en Flutter, al dibujar. Verificados
renderizando la app real.

| Síntoma | Causa | Solución |
|---|---|---|
| Una vista entera sale **gris** | La vista hereda de `ft.Container` y guarda un atributo propio con nombre de propiedad de Flet: `self.left = ft.Column(...)`. `left` es la posición absoluta (un número); Flet envía la `Column` como posición y Flutter no puede dibujar | Nunca nombrar atributos propios `left`, `top`, `right`, `bottom`, `width`, `height`, `data`, `key`, `content`, `visible`, `opacity`, `scale`, `rotate`, `offset`, `margin`, `padding`, `alignment`, `tooltip`, `badge`, `disabled`… Usar sufijos claros (`self.left_col`, `self.panel_izq`). Detectarlo con el script de abajo |
| Un `Canvas` (o lo que hay dentro) **aparece un instante y desaparece**; el cliente reporta `"colors" must have length 2 if "colorStops" is omitted` | `ft.PaintLinearGradient` / `ft.PaintRadialGradient` (los degradados de `ft.Paint`, usados en Canvas) con **más de 2 colores** sin `color_stops` | Pasar siempre `color_stops=[0.0, 0.5, 1.0]` (uno por color). Los `ft.LinearGradient`/`ft.RadialGradient` de `Container` **sí** admiten 3+ colores sin posiciones |
| Hueco vacío debajo de un `Dropdown` (u otro control) | `expand=True` en un hijo de `Column` lo estira en **vertical**, no en horizontal | Ancho completo: `Dropdown(expanded_insets=ft.Padding.all(0))`, o `Column(horizontal_alignment=ft.CrossAxisAlignment.STRETCH)`. Reservar `expand` para repartir el eje principal de su `Row`/`Column` |
| Botones a todo el ancho, uno encima del otro | `Row(wrap=True)` se convierte en un `Wrap`: ahí `expand` se ignora y un `Container` con `alignment=` ocupa todo el ancho disponible | Para filas de botones usar `Row` normal (sin `wrap`), o quitar `alignment` del botón |

Regla general de Flutter (no aislada en esta app, pero conviene
respetarla): `Row(vertical_alignment=STRETCH)` necesita un alto acotado.
Si la fila no tiene `height` ni `expand` y está dentro de una `Column`,
usar `intrinsic_height=True` para que tome el alto de su celda más alta.

Reglas de `expand` (código Dart de Flet 1.0): solo tiene efecto si el
padre es `Row`, `Column` o `View`. En un `Container`, `Stack` o `Canvas`
se ignora, y en un `Row(wrap=True)` también.

Detectar atributos que chocan con propiedades de Flet, antes de entregar:
```python
import ast, glob, flet as ft
campos = set(ft.Container.__dataclass_fields__) | {n for n in dir(ft.Container) if not n.startswith("_")}
permitidos = {"content", "expand", "padding", "bgcolor", "border", "border_radius",
              "shadow", "gradient", "animate", "on_click", "on_hover"}  # se asignan a propósito
for ruta in glob.glob("views/**/*.py", recursive=True) + glob.glob("components/*.py"):
    for clase in [n for n in ast.walk(ast.parse(open(ruta).read())) if isinstance(n, ast.ClassDef)]:
        attrs = {t.attr for n in ast.walk(clase) if isinstance(n, ast.Assign) for t in n.targets
                 if isinstance(t, ast.Attribute) and getattr(t.value, "id", "") == "self"}
        if choque := sorted((attrs & campos) - permitidos):
            print(ruta, clase.name, choque)
```

**Canvas con borde decorativo** (por ejemplo, un borde punteado
`stroke_dash_pattern`, que `ft.Border` no soporta): poner el `Canvas`
como capa de fondo en un `Stack` (`left=0, top=0, right=0, bottom=0`),
el contenido en otra capa, y en `on_resize` actualizar **solo** el
canvas (`canvas.update()`), así redibujar el borde nunca toca el contenido.

### 20. Ver el error real cuando algo no se dibuja

1. Agregar en `main`: `page.on_error = lambda e: print("ERROR CLIENTE:", e.data)`.
   El cliente Flutter envía a Python los errores de dibujo con el
   mensaje exacto. Es lo primero que hay que mirar ante una pantalla gris.
2. `flet run -v main.py` también muestra el log de Flet.
3. Si no hay acceso a la máquina del usuario, renderizar la app real en
   Linux con `flet-desktop` + `Xvfb` y tomar capturas. El procedimiento
   completo (instalación, arnés que recorre la app, bisección de una
   vista) está en `references/depuracion-render-real.md`.

No adivinar causas visuales a partir del código ni dar "arreglos"
sin verificar: medir con `on_error` o con capturas reales primero.

### 21. Otros detalles verificados

- `Container.on_hover`: `e.data` puede llegar como `bool` o como el texto `"true"`/`"false"` → comparar con `e.data in (True, "true")`.
- `ReorderableListView.on_reorder`: `item = lista.pop(e.old_index)` y luego `lista.insert(e.new_index, item)` (el `new_index` ya viene ajustado; es el ejemplo oficial).
- No existe un evento para **soltar archivos desde el Explorador del sistema** en Flet 1.0 (`DragTarget` solo funciona entre controles de la propia app). No prometer "arrastra y suelta" en la interfaz: ofrecer botones de elegir archivos/carpeta.

## Empaquetado (`flet build`) — novedades y errores ya resueltos en 1.0.0

- Usar `flet clean` en vez de la flag `--clear-cache` (eliminada, estaba deprecada desde 0.86.0).
- **Icono único para todo**: basta con proveer un `assets/icon.png` **full-bleed** (sin márgenes) — Flet calcula automáticamente el recorte/margen correcto para cada plataforma (iOS 60%, macOS 68% con squircle, Android 85% del radio del círculo de máscara, web/Windows/Linux sin máscara). Proveer `icon_ios.png`, `icon_macos.png` o `icon_android.png` explícitos si se quiere optar por un icono manual en esa plataforma en vez del recorte automático.
- `[tool.flet] icon_background` controla el color detrás del icono donde la transparencia no puede sobrevivir (iOS, tile de macOS, iconos maskable de web); tiene fallback desde/hacia `[tool.flet.android] adaptive_icon_background`.
- `flet build linux` ahora genera icono y entrada de escritorio (`.desktop`) reales — antes el icono se ignoraba silenciosamente en Linux.
- `flet build macos` soporta firma de código, notarización y builds para Mac App Store vía `--macos-distribution` (`developer-id` o `app-store`), con auto-detección de certificados en el keychain.
- Splash: las claves bajo `[tool.flet.splash]` se renombraron (`icon_bgcolor` → `icon_background`, `icon_dark_bgcolor` → `icon_dark_background`, `android_12_fit` → `icon_fit`); los nombres viejos siguen funcionando pero usar los nuevos en código nuevo.
- `flet build web --no-cdn` ahora sí evita descargar Pyodide desde CDN (antes lo descargaba igual por un bug de comparación de strings).
- `flet run -v` y `-vv` ahora sí activan logging real de Flet (antes no hacían nada).

### Tabla de errores de empaquetado móvil ya resueltos o con solución conocida

| Error / síntoma | Causa | Solución |
|---|---|---|
| `ReadTimeoutError` descargando el template de build | Red/firewall/antivirus cortando la descarga | Reintentar; revisar proxy corporativo; excluir la carpeta del antivirus |
| `ModuleNotFoundError: No module named 'certifi'` en pantalla blanca (Android) | Bug de empaquetado; `requirements.txt` viejo pisando `pyproject.toml` | Agregar `certifi` explícito a `dependencies`; borrar `requirements.txt` suelto en la raíz |
| `Unknown control: BarChart/LineChart` en el celular | `fl_chart` no quedó registrado en el build | `flet clean` (no solo limpiar caché parcial) y recompilar desde cero |
| `FilePicker.save_file()` poco confiable en Android nativo | Limitación de plataforma en el empaquetado móvil | Preferir `ft.Share()` para "guardar/enviar" en Android; el diálogo de guardado sí es confiable en desktop |
| `FilePicker.pick_files()`, `Clipboard`, `Share` no hacen nada en **web + iOS Safari** | El navegador solo permite estas operaciones dentro del gesto original del click | Usar `action=ft.PickFiles(...)` / `ft.CopyToClipboard(...)` / `ft.ShareText(...)` en vez de llamar al servicio desde el handler (ver sección 1) |
| `No profile for team 'X' matching 'Y' found` (iOS, tarde, en Xcode) | Perfil de aprovisionamiento mal configurado | `flet build ipa` ahora valida el perfil **antes** de compilar y lista los perfiles instalados si falla |

## Al recibir un pedido de "hazme una app en Flet"

1. Confirmar que se trabaja contra **Flet 1.0.0** (o preguntar si el usuario necesita otra versión explícitamente); si el usuario pega código viejo con `ft.app(...)`, `ElevatedButton`, `page.clipboard`, `ConstrainedControl`, `Page.go()`, etc., migrarlo a las formas de 1.0.0 de esta guía como parte del trabajo, sin que haga falta que lo pida.
2. Preguntar (si no es obvio del contexto) qué tan grande es: ¿una pantalla o varias? Si son varias, usar la arquitectura modular de arriba desde el inicio, no un solo archivo.
3. Si la app va a correr como web y necesita compartir, copiar al portapapeles, abrir URLs o seleccionar archivos desde un click, usar `action=` (sección 1) en vez de llamar al servicio desde el handler, para que funcione también en iOS Safari.
4. Para controles, parámetros, enums o íconos **no cubiertos en esta guía**, resolver todas las dudas en una sola llamada `fletapi.py q ...` antes de escribir el código (no confiar en memoria de entrenamiento ni en ejemplos de internet). Al terminar, correr `fletapi.py check` una vez sobre el proyecto y corregir lo que reporte.
5. Probar la construcción de la app con un `FakePage` + monkeypatch antes de entregar el código, simulando el flujo completo (crear, guardar, navegar, editar, eliminar) con datos de ejemplo.
6. Si el trabajo incluye diseño visual (layouts, Canvas, degradados, temas), además: correr el detector de atributos de la sección 19, dejar `page.on_error` activo durante el desarrollo y, cuando sea posible, renderizar la app real y revisar capturas de cada pantalla en modo claro y oscuro (`references/depuracion-render-real.md`). Si no se pudo renderizar, decirlo con claridad al entregar en vez de dar el diseño por verificado.
7. Entregar también `pyproject.toml`/`requirements.txt` con las versiones exactas fijadas (`==`), y mencionar si el proyecto va a compilarse a APK/AAB/IPA para adelantarse a los gotchas de la tabla de arriba.
8. Recordar la regla de persistencia (sección 12): ningún dato crítico debe depender de código que corre "al cerrar" la app.
