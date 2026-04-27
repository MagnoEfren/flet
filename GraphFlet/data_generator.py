"""
data_generator.py
Genera datos industriales realistas y los exporta a Excel.
"""

import random
import math
from datetime import datetime, timedelta
import pandas as pd


# ──────────────────────────────────────────────
# Constantes de simulación industrial
# ──────────────────────────────────────────────
HORAS = 24          # ventana de datos: últimas 24 horas
PUNTOS = 48         # 1 lectura cada 30 min


def _suavizar(valores: list[float], factor: float = 0.3) -> list[float]:
    """Aplica suavizado exponencial para simular variación real de sensores."""
    resultado = [valores[0]]
    for v in valores[1:]:
        resultado.append(resultado[-1] * (1 - factor) + v * factor)
    return resultado


class DataGenerator:
    """Genera y almacena todos los conjuntos de datos industriales."""

    def __init__(self):
        base_ts = datetime(2026, 4, 26, 0, 0, 0)
        self.timestamps = [
            base_ts + timedelta(minutes=30 * i) for i in range(PUNTOS)
        ]
        self._generar()

    # ── Generadores individuales ──────────────────

    def _gen_temperatura(self) -> list[float]:
        """Temperatura de horno industrial (°C). Rango: 180–240 °C."""
        base = 210.0
        raw = [
            base
            + 15 * math.sin(2 * math.pi * i / 24)   # ciclo térmico diario
            + random.gauss(0, 2)                      # ruido sensor
            + (8 if 16 <= i <= 20 else 0)             # pico de producción tarde
            for i in range(PUNTOS)
        ]
        return [round(v, 2) for v in _suavizar(raw, 0.4)]

    def _gen_presion(self) -> list[float]:
        """Presión de línea hidráulica (bar). Rango: 4.5–7.5 bar."""
        base = 6.0
        raw = [
            base
            + 0.8 * math.sin(2 * math.pi * i / 12)
            + random.gauss(0, 0.15)
            + (0.6 if random.random() < 0.05 else 0)  # micro-picos esporádicos
            for i in range(PUNTOS)
        ]
        return [round(max(4.0, min(8.0, v)), 3) for v in _suavizar(raw, 0.25)]

    def _gen_vibracion(self) -> list[float]:
        """Vibración de rodamientos (mm/s RMS). Rango: 0.5–4.5 mm/s."""
        base = 1.8
        raw = [
            base
            + 0.5 * math.sin(2 * math.pi * i / 8)
            + random.gauss(0, 0.2)
            + (1.5 if 30 <= i <= 33 else 0)            # anomalía simulada
            for i in range(PUNTOS)
        ]
        return [round(max(0.1, v), 3) for v in _suavizar(raw, 0.35)]

    def _gen_energia(self) -> list[float]:
        """Consumo energético (kWh). Rango: 45–95 kWh por intervalo."""
        base = 65.0
        raw = [
            base
            + 18 * math.sin(2 * math.pi * i / 24 - math.pi / 4)
            + random.gauss(0, 3)
            + (10 if 14 <= i <= 22 else -8 if i < 6 else 0)
            for i in range(PUNTOS)
        ]
        return [round(max(30.0, v), 2) for v in _suavizar(raw, 0.3)]

    def _gen_produccion(self) -> list[float]:
        """Unidades producidas por hora. Rango: 0–180 uds."""
        base = 120.0
        raw = [
            base
            + 30 * math.sin(2 * math.pi * i / 24)
            + random.gauss(0, 8)
            + (-120 if i < 4 or i >= 44 else 0)        # turno nocturno parado
            for i in range(PUNTOS)
        ]
        return [round(max(0.0, v), 1) for v in _suavizar(raw, 0.2)]

    def _generar(self):
        self.temperatura = self._gen_temperatura()
        self.presion = self._gen_presion()
        self.vibracion = self._gen_vibracion()
        self.energia = self._gen_energia()
        self.produccion = self._gen_produccion()

    # ── Acceso a datos ────────────────────────────

    def get_series(self, nombre: str) -> list[float]:
        return getattr(self, nombre, [])

    def get_timestamps_str(self) -> list[str]:
        return [t.strftime("%H:%M") for t in self.timestamps]

    def get_resumen_pie(self) -> dict:
        """
        Porcentaje de distribución energética por área de planta.
        Datos representativos para PieChart.
        """
        return {
            "Hornos":       35.4,
            "Compresores":  22.1,
            "Iluminación":  10.8,
            "HVAC":         18.3,
            "Otros":        13.4,
        }

    def get_produccion_por_turno(self) -> dict[str, float]:
        """Producción agrupada por turno para BarChart."""
        # Turno mañana: índices 8–23 (04:00-12:00), tarde: 24-35, noche: 36-47+0-7
        mañana = sum(self.produccion[8:24])
        tarde  = sum(self.produccion[24:36])
        noche  = sum(self.produccion[36:]) + sum(self.produccion[:8])
        return {"Mañana": round(mañana, 1), "Tarde": round(tarde, 1), "Noche": round(noche, 1)}

    # ── Exportación Excel ─────────────────────────

    def exportar_excel(self, ruta: str = "industrial_data.xlsx") -> str:
        """Crea el archivo Excel con 5 hojas de datos."""
        ts_str = [t.strftime("%Y-%m-%d %H:%M:%S") for t in self.timestamps]

        hojas = {
            "temperatura": pd.DataFrame({
                "timestamp": ts_str,
                "temperatura_C": self.temperatura,
                "limite_inferior": [180.0] * PUNTOS,
                "limite_superior": [240.0] * PUNTOS,
            }),
            "presion": pd.DataFrame({
                "timestamp": ts_str,
                "presion_bar": self.presion,
                "setpoint": [6.0] * PUNTOS,
            }),
            "vibracion": pd.DataFrame({
                "timestamp": ts_str,
                "vibracion_mm_s": self.vibracion,
                "umbral_alerta": [3.5] * PUNTOS,
            }),
            "energia": pd.DataFrame({
                "timestamp": ts_str,
                "consumo_kWh": self.energia,
                "consumo_acumulado_kWh": pd.Series(self.energia).cumsum().round(2).tolist(),
            }),
            "produccion": pd.DataFrame({
                "timestamp": ts_str,
                "unidades_hora": self.produccion,
                "objetivo": [130.0] * PUNTOS,
                "eficiencia_pct": [
                    round(min(100, p / 1.3), 1) for p in self.produccion
                ],
            }),
        }

        with pd.ExcelWriter(ruta, engine="openpyxl") as writer:
            for nombre, df in hojas.items():
                df.to_excel(writer, sheet_name=nombre, index=False)
                # Ajustar ancho de columnas
                ws = writer.sheets[nombre]
                for col in ws.columns:
                    max_len = max(len(str(cell.value) or "") for cell in col)
                    ws.column_dimensions[col[0].column_letter].width = max_len + 4

        return ruta
