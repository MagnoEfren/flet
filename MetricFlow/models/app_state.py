"""
models/app_state.py — Estado compartido entre vistas (singleton).
Todos los datos son de ejemplo (mock), pensados para mostrar el diseño
funcionando; services/data_service.py es el lugar natural para
reemplazarlos por datos reales (BD, API) más adelante.
"""


class AppState:
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self):
        self.usuario_nombre = "Carlos Medina"
        self.usuario_rol = "Administrador"
        self.fecha_actual = "Mié, 29 May 2024"

        # ---------- Dashboard: métricas principales ----------
        self.metricas = [
            {"titulo": "Ingresos Totales", "valor": "$ 24,500", "delta": 12.5, "positivo": True},
            {"titulo": "Pedidos Totales", "valor": "1,240", "delta": 8.2, "positivo": True},
            {"titulo": "Nuevos Clientes", "valor": "320", "delta": -4.3, "positivo": False},
            {"titulo": "Tasa de Conversión", "valor": "3.2 %", "delta": 2.1, "positivo": True},
        ]
        self.rango_fechas = "Del 01 Jun, 2024 al 29 Jun, 2024"

        # ---------- Pedidos por hora (heatmap) ----------
        self.horas_heatmap = ["9 am", "10 am", "11 am", "12 pm", "1 pm", "2 pm", "3 pm"]
        self.dias_heatmap = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        # niveles: 0=sin datos, 1=200+, 2=500+, 3=1000+, 4=2000+
        self.matriz_heatmap = [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0, 0, 0],
            [1, 3, 3, 3, 1, 0, 0],
            [2, 4, 4, 4, 2, 1, 0],
            [1, 3, 3, 3, 1, 0, 0],
            [0, 1, 2, 1, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0],
        ]

        # ---------- Rendimiento de ventas mensual (línea) ----------
        self.meses_ventas = ["Ene", "Feb", "Mar", "Abr", "May", "Jun"]
        self.serie_ventas = [3200, 4100, 3500, 4790, 3900, 4600]
        self.serie_meta = [3800, 3600, 4200, 3830, 4100, 4000]
        self.punto_destacado = {"mes": "1 Abr, 2025", "ventas": 4790, "meta": 3830}

        # ---------- Ventas por país ----------
        self.ventas_pais = [
            {"pais": "Reino Unido", "bandera": "🇬🇧", "productos": "6.3K"},
            {"pais": "Indonesia", "bandera": "🇮🇩", "productos": "5.2K"},
            {"pais": "Malasia", "bandera": "🇲🇾", "productos": "4.7K"},
            {"pais": "China", "bandera": "🇨🇳", "productos": "4.5K"},
            {"pais": "Tailandia", "bandera": "🇹🇭", "productos": "3.2K"},
            {"pais": "Filipinas", "bandera": "🇵🇭", "productos": "2.9K"},
        ]

        # ---------- Top productos ----------
        self.top_productos = [
            {"producto": "MagStand Pro 1", "ingresos": "$24,500", "ventas": 846, "crecimiento": 32, "resenas": 570, "vistas": 978},
            {"producto": "MagStand Pro 2", "ingresos": "$16,300", "ventas": 598, "crecimiento": 26, "resenas": 385, "vistas": 945},
            {"producto": "MagStand Pro 3", "ingresos": "$12,980", "ventas": 389, "crecimiento": 13, "resenas": 127, "vistas": 437},
            {"producto": "MagStand Pro 4", "ingresos": "$10,984", "ventas": 265, "crecimiento": -11, "resenas": 190, "vistas": 265},
        ]

        # ---------- Órdenes ----------
        self.ordenes = [
            {"id": "#ORD-2481", "cliente": "Laura Gómez", "producto": "MagStand Pro 1", "fecha": "28 Jun 2024", "estado": "Entregado", "total": "$245.00"},
            {"id": "#ORD-2480", "cliente": "Andrés Ruiz", "producto": "MagStand Pro 3", "fecha": "28 Jun 2024", "estado": "En camino", "total": "$132.50"},
            {"id": "#ORD-2479", "cliente": "Marta Solís", "producto": "MagStand Pro 2", "fecha": "27 Jun 2024", "estado": "Procesando", "total": "$89.00"},
            {"id": "#ORD-2478", "cliente": "Diego Vargas", "producto": "MagStand Pro 4", "fecha": "27 Jun 2024", "estado": "Cancelado", "total": "$54.90"},
            {"id": "#ORD-2477", "cliente": "Sofía Herrera", "producto": "MagStand Pro 1", "fecha": "26 Jun 2024", "estado": "Entregado", "total": "$245.00"},
            {"id": "#ORD-2476", "cliente": "Julián Peña", "producto": "MagStand Pro 2", "fecha": "26 Jun 2024", "estado": "En camino", "total": "$89.00"},
        ]

        # ---------- Productos ----------
        self.productos = [
            {"nombre": "MagStand Pro 1", "categoria": "Soportes", "precio": "$24.90", "stock": 128, "ventas": 846},
            {"nombre": "MagStand Pro 2", "categoria": "Soportes", "precio": "$19.90", "stock": 76, "ventas": 598},
            {"nombre": "MagStand Pro 3", "categoria": "Accesorios", "precio": "$33.00", "stock": 12, "ventas": 389},
            {"nombre": "MagStand Pro 4", "categoria": "Accesorios", "precio": "$41.40", "stock": 0, "ventas": 265},
            {"nombre": "MagStand Mini", "categoria": "Soportes", "precio": "$14.50", "stock": 203, "ventas": 512},
        ]

        # ---------- Clientes ----------
        self.clientes = [
            {"nombre": "Laura Gómez", "correo": "laura.gomez@mail.com", "pais": "🇪🇸 España", "pedidos": 14, "gastado": "$1,240"},
            {"nombre": "Andrés Ruiz", "correo": "andres.ruiz@mail.com", "pais": "🇲🇽 México", "pedidos": 9, "gastado": "$860"},
            {"nombre": "Marta Solís", "correo": "marta.solis@mail.com", "pais": "🇦🇷 Argentina", "pedidos": 5, "gastado": "$412"},
            {"nombre": "Diego Vargas", "correo": "diego.vargas@mail.com", "pais": "🇵🇪 Perú", "pedidos": 21, "gastado": "$2,150"},
            {"nombre": "Sofía Herrera", "correo": "sofia.herrera@mail.com", "pais": "🇨🇴 Colombia", "pedidos": 3, "gastado": "$198"},
        ]

        # ---------- Analítica ----------
        self.resumen_analitica = [
            {"titulo": "Visitantes", "valor": "48,204", "delta": 6.4, "positivo": True},
            {"titulo": "Tasa de Rebote", "valor": "38.2 %", "delta": -1.8, "positivo": True},
            {"titulo": "Tiempo Promedio", "valor": "4m 12s", "delta": 3.5, "positivo": True},
        ]
        self.ventas_por_categoria = [
            {"categoria": "Soportes", "valor": 4200},
            {"categoria": "Accesorios", "valor": 3100},
            {"categoria": "Fundas", "valor": 2400},
            {"categoria": "Cables", "valor": 1800},
            {"categoria": "Otros", "valor": 900},
        ]

        # ---------- Navegación ----------
        self.pestaña_activa = "dashboard"


def get_state() -> AppState:
    return AppState()
