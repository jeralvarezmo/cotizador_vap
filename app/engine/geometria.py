"""Cálculos geométricos PUROS (sin Flask ni base de datos).

Las medidas son Decimal expresadas en METROS (unidad interna provisional;
la unidad definitiva del negocio está PENDIENTE DE CONFIRMAR).
"""
from decimal import ROUND_HALF_UP, Decimal

_CUATRO_DECIMALES = Decimal("0.0001")


def calcular_area(ancho, alto):
    """Área de un rectángulo en m²."""
    return (ancho * alto).quantize(_CUATRO_DECIMALES, rounding=ROUND_HALF_UP)


def calcular_perimetro(ancho, alto):
    """Perímetro de un rectángulo en metros."""
    return (2 * (ancho + alto)).quantize(_CUATRO_DECIMALES, rounding=ROUND_HALF_UP)
