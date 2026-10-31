"""Precio, recargo/margen y manejo de dinero (PURO: sin Flask ni base de datos).

El dinero se maneja en CENTAVOS enteros para evitar errores de coma flotante.

IMPORTANTE: "recargo sobre el costo" y "margen sobre el precio de venta" NO son lo
mismo. Con costo = Q1,850 y un 30 %:
    recargo sobre costo  -> 1,850 x 1.30  = Q2,405.00
    margen sobre precio  -> 1,850 / 0.70  = Q2,642.86
La base real que usa el negocio está PENDIENTE DE CONFIRMAR.
"""
from decimal import ROUND_HALF_UP, Decimal

BASE_RECARGO = "recargo_sobre_costo"
BASE_MARGEN = "margen_sobre_precio"


def redondear_centavos(valor):
    """Redondea (mitad hacia arriba) a un entero de centavos."""
    return int(Decimal(valor).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def formato_q(centavos):
    """185000 -> 'Q1,850.00'."""
    return f"Q{Decimal(int(centavos)) / 100:,.2f}"


def porcentaje_sobre(parte, base):
    """parte / base en %, con un decimal. None si la base es 0."""
    if not base:
        return None
    return (Decimal(parte) * 100 / Decimal(base)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def calcular_precio(costo_total_c, porcentaje, base=BASE_RECARGO):
    """Precio ofertado y utilidad estimada a partir del costo total (centavos)."""
    costo = Decimal(int(costo_total_c))
    p = Decimal(str(porcentaje))
    if p < 0:
        raise ValueError("El porcentaje no puede ser negativo.")
    if base == BASE_RECARGO:
        precio = costo * (1 + p / 100)
    elif base == BASE_MARGEN:
        if p >= 100:
            raise ValueError("El margen sobre el precio debe ser menor a 100 %.")
        precio = costo / (1 - p / 100)
    else:
        raise ValueError("Base de cálculo desconocida.")
    precio_c = redondear_centavos(precio)
    utilidad_c = precio_c - int(costo_total_c)
    return {
        "precio_c": precio_c,
        "utilidad_c": utilidad_c,
        "utilidad_sobre_costo": porcentaje_sobre(utilidad_c, costo_total_c),
        "utilidad_sobre_precio": porcentaje_sobre(utilidad_c, precio_c),
    }


def repartir_proporcional(total_c, pesos):
    """Reparte un total (centavos) en proporción a 'pesos'; la suma siempre es exacta."""
    n = len(pesos)
    if n == 0:
        return []
    suma = sum(pesos)
    if suma == 0:
        partes = [total_c // n] * n
    else:
        partes = [redondear_centavos(Decimal(total_c) * Decimal(p) / Decimal(suma)) for p in pesos]
    partes[-1] += total_c - sum(partes)  # el último absorbe el redondeo
    return partes
