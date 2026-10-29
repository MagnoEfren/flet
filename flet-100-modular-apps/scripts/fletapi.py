#!/usr/bin/env python3
"""Verificador compacto de la API de Flet 1.0.0 usando el índice de flet-mcp==1.0.0.

Pensado para gastar pocos tokens: una sola llamada resuelve muchas dudas y
`check` solo imprime los problemas encontrados.

Uso:
  python3 fletapi.py check RUTA [RUTA...]   # revisa .py: ft.X inexistentes, Enum.MIEMBRO, kwargs
  python3 fletapi.py q CONSULTA [CONSULTA...]
      X              resumen de X: tipo, paquete, propiedades y eventos (incluye heredados)
      X.miembro      documentación completa de un miembro (ej. Dropdown.on_select)
      Enum.MIEMBRO   ¿existe? (ej. Icons.HOME, BoxFit.COVER)
      icon:palabra   buscar íconos por concepto (ej. icon:usuario -> usar inglés: icon:user)
      ex:texto       buscar ejemplos oficiales      exget:ID   ver un ejemplo
      cli:comando    ayuda de la CLI (ej. cli:build)
"""
import ast
import asyncio
import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

VERSION = "1.0.0"


def _cargar_flet_mcp():
    try:
        return importlib.import_module("flet_mcp")
    except ImportError:
        pass
    base = [sys.executable, "-m", "pip", "install", "-q", f"flet-mcp=={VERSION}"]
    r = subprocess.run(base, capture_output=True, text=True)
    if r.returncode != 0:
        subprocess.run(base + ["--break-system-packages"], capture_output=True, text=True)
    importlib.invalidate_caches()
    return importlib.import_module("flet_mcp")


def _indice():
    os.environ.setdefault("FLET_MCP_ENABLE_EXAMPLES", "1")
    os.environ.setdefault("FLET_MCP_ENABLE_CLI", "1")
    mod = _cargar_flet_mcp()
    datos = json.loads((Path(mod.__file__).parent / "data" / "api.json").read_text())
    idx = {}
    for grupo in ("controls", "types", "events", "enums", "functions"):
        for item in datos[grupo]:
            idx.setdefault(item["name"], (grupo, item))
    return mod, idx


def _miembros(idx, nombre, _visto=None):
    """Propiedades + eventos de `nombre` incluyendo bases. Devuelve (set, completo?)."""
    _visto = _visto or set()
    if nombre in _visto:
        return set(), True
    _visto.add(nombre)
    if nombre not in idx:
        return set(), False
    _, item = idx[nombre]
    nombres = {p["name"] for p in item.get("properties", []) + item.get("events", [])}
    completo = True
    for base in item.get("bases") or []:
        base = base.split(".")[-1]
        if base in ("object", "Generic", "ABC", "Enum", "IntEnum", "str"):
            continue
        sub, ok = _miembros(idx, base, _visto)
        nombres |= sub
        completo &= ok
    return nombres | SIEMPRE, completo


# Campos de BaseControl que el índice no lista pero todo control acepta.
SIEMPRE = {"data", "key", "ref"}


def _definido_en(idx, nombre, miembro, _visto=None):
    """Clase (propia o base) donde se declara `miembro`."""
    _visto = _visto or set()
    if nombre in _visto or nombre not in idx:
        return None
    _visto.add(nombre)
    item = idx[nombre][1]
    if miembro in {p["name"] for p in item.get("properties", []) + item.get("events", []) + item.get("methods", [])}:
        return nombre
    for base in item.get("bases") or []:
        r = _definido_en(idx, base.split(".")[-1], miembro, _visto)
        if r:
            return r
    return None


def _es_enum(idx, nombre):
    return nombre in idx and idx[nombre][0] == "enums"


def _miembros_enum(idx, nombre):
    return {m["name"] for m in idx[nombre][1].get("members", [])}


# ---------------------------------------------------------------- check
def check(rutas):
    _, idx = _indice()
    archivos = []
    for r in rutas:
        p = Path(r)
        archivos += sorted(p.rglob("*.py")) if p.is_dir() else [p]
    archivos = [a for a in archivos if not any(x in a.parts for x in ("build", ".venv", "venv", "__pycache__"))]
    indexados = {item.get("package") for _, item in idx.values()}
    sin_indice = set()
    problemas = 0
    for archivo in archivos:
        try:
            arbol = ast.parse(archivo.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError) as e:
            print(f"{archivo}: no se pudo leer ({e})")
            problemas += 1
            continue
        alias = set()
        for n in ast.walk(arbol):
            if isinstance(n, ast.Import):
                for a in n.names:
                    paquete = a.name.split(".")[0].replace("_", "-")
                    if not paquete.startswith("flet"):
                        continue
                    if paquete in indexados:
                        alias.add(a.asname or a.name)
                    else:
                        sin_indice.add(paquete)
        if not alias:
            continue
        vistos = set()

        def reportar(linea, msg):
            nonlocal problemas
            if (linea, msg) not in vistos:
                vistos.add((linea, msg))
                problemas += 1
                print(f"{archivo}:{linea}: {msg}")

        for n in ast.walk(arbol):
            # ft.Nombre  /  ft.Enum.MIEMBRO
            if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id in alias:
                nombre = n.attr
                if nombre[:1].isupper() and nombre not in idx:
                    reportar(n.lineno, f"{n.value.id}.{nombre} no existe en Flet {VERSION}")
            if (isinstance(n, ast.Attribute) and isinstance(n.value, ast.Attribute)
                    and isinstance(n.value.value, ast.Name) and n.value.value.id in alias):
                enum, miembro = n.value.attr, n.attr
                if _es_enum(idx, enum) and miembro.isupper() and miembro not in _miembros_enum(idx, enum):
                    reportar(n.lineno, f"{enum}.{miembro} no existe")
            # ft.Control(kwarg=...)
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and isinstance(n.func.value, ast.Name) and n.func.value.id in alias):
                nombre = n.func.attr
                if nombre in idx and idx[nombre][0] in ("controls", "types"):
                    validos, completo = _miembros(idx, nombre)
                    if not completo or not (validos - SIEMPRE):
                        continue
                    for kw in n.keywords:
                        if kw.arg and kw.arg not in validos:
                            reportar(n.lineno, f"{nombre}({kw.arg}=...) parámetro desconocido")
    if sin_indice:
        print("sin índice (no verificado, usar inspect): " + ", ".join(sorted(sin_indice)))
    print(f"OK: {len(archivos)} archivos, sin problemas" if not problemas else f"-- {problemas} problema(s)")
    return 1 if problemas else 0


# ---------------------------------------------------------------- q
async def _consultas(mod, idx, consultas):
    from fastmcp import Client

    async with Client(mod.mcp) as c:
        async def tool(nombre, args):
            r = await c.call_tool(nombre, args, raise_on_error=False)
            return "\n".join(getattr(x, "text", "") for x in r.content)

        for q in consultas:
            print(f"## {q}")
            if q.startswith("icon:"):
                print(await tool("find_icon", {"query": q[5:], "limit": 8}))
            elif q.startswith("ex:"):
                print((await tool("search_examples", {"query": q[3:], "limit": 5}))[:1500])
            elif q.startswith("exget:"):
                print(await tool("get_example", {"example_id": q[6:]}))
            elif q.startswith("cli:"):
                print((await tool("get_cli_help", {"command": q[4:] or None}))[:2500])
            elif "." in q:
                a, b = q.split(".", 1)
                if _es_enum(idx, a) and b.isupper():
                    if b in _miembros_enum(idx, a):
                        print("existe")
                    else:
                        raiz = b.split("_")[0][: max(3, len(b.split("_")[0]) - 1)]
                        print("NO existe. Similares: "
                              + await tool("search_enum_members", {"name": a, "query": raiz, "limit": 8}))
                else:
                    duenio = _definido_en(idx, a, b) or a
                    if duenio != a:
                        print(f"(heredado de {duenio})")
                    print((await tool("get_api", {"name": duenio, "member": b}))[:2000])
            elif q not in idx:
                print(f"NO existe en Flet {VERSION}")
            else:
                grupo, item = idx[q]
                if grupo == "enums":
                    m = [x["name"] for x in item.get("members", [])]
                    print(f"enum ({len(m)}): " + (", ".join(m) if len(m) <= 60 else "grande; usa Enum.MIEMBRO o icon:"))
                    continue
                print(f"{item.get('kind', grupo)} | paquete {item.get('package')} | bases {item.get('bases')}")
                propios_p = [p["name"] for p in item.get("properties", [])]
                propios_e = [p["name"] for p in item.get("events", [])]
                metodos = [m["name"] + ("()*" if m.get("async") else "()") for m in item.get("methods", [])]
                todos, _ = _miembros(idx, q)
                heredados = sorted(todos - set(propios_p) - set(propios_e))
                print("props:", ", ".join(propios_p))
                if propios_e:
                    print("eventos:", ", ".join(propios_e))
                if metodos:
                    print("métodos (* = async):", ", ".join(metodos))
                if heredados:
                    print("heredados:", ", ".join(heredados))


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("check", "q"):
        print(__doc__)
        return 2
    if sys.argv[1] == "check":
        return check(sys.argv[2:])
    mod, idx = _indice()
    asyncio.run(_consultas(mod, idx, sys.argv[2:]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
