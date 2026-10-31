"""Costo de materiales de un elemento a partir de una receta (PURO).

Recibe datos simples (listas y diccionarios), no objetos de base de datos.
Las recetas son de DEMOSTRACIÓN: las reglas reales de fabricación están
PENDIENTES DE CONFIRMAR con el experto del negocio.
"""
from decimal import ROUND_HALF_UP, Decimal

from .geometria import calcular_area, calcular_perimetro
from .precios import redondear_centavos

TEXTO_REGLA = {
    "perimetro": "perímetro (m)",
    "area": "área (m²)",
    "ancho": "ancho (m)",
    "alto": "alto (m)",
    "fijo": "cantidad fija",
    "por_hoja": "nº de hojas",
}


def cantidad_base(regla, factor, area, perimetro, ancho, alto, hojas):
    """Cantidad de un componente para UNA unidad del producto, sin desperdicio."""
    magnitudes = {
        "perimetro": perimetro,
        "area": area,
        "ancho": ancho,
        "alto": alto,
        "fijo": Decimal(1),
        "por_hoja": Decimal(hojas),
    }
    if regla not in magnitudes:
        raise ValueError(f"Regla de cantidad desconocida: {regla}")
    return magnitudes[regla] * factor


def calcular_item(componentes, ancho, alto, cantidad, hojas):
    """Calcula área, perímetro y el desglose de materiales de un elemento.

    componentes: lista de dicts con etiqueta, rol, regla, factor, desperdicio_pct y
                 material {id, nombre, unidad, precio_centavos, es_demo}.
    ancho, alto: Decimal en metros.  cantidad, hojas: enteros.
    """
    area = calcular_area(ancho, alto)
    perimetro = calcular_perimetro(ancho, alto)
    lineas = []
    costo_materiales_c = 0
    for c in componentes:
        factor = Decimal(str(c["factor"]))
        desperdicio = Decimal(str(c["desperdicio_pct"]))
        base = cantidad_base(c["regla"], factor, area, perimetro, ancho, alto, hojas)
        total = (base * (1 + desperdicio / 100) * cantidad).quantize(
            Decimal("0.0001"), rounding=ROUND_HALF_UP
        )
        m = c["material"]
        subtotal_c = redondear_centavos(total * m["precio_centavos"])
        lineas.append(
            {
                "concepto": c["etiqueta"],
                "rol": c["rol"],
                "material_id": m["id"],
                "material_nombre": m["nombre"],
                "unidad": m["unidad"],
                "cantidad": total,
                "precio_unit_c": m["precio_centavos"],
                "subtotal_c": subtotal_c,
                "es_demo": 1 if m.get("es_demo") else 0,
                "regla_texto": f"{TEXTO_REGLA[c['regla']]} × {factor.normalize():f}"
                + (f" + {desperdicio.normalize():f} % de desperdicio" if desperdicio else ""),
            }
        )
        costo_materiales_c += subtotal_c
    return {
        "area": area,
        "perimetro": perimetro,
        "lineas": lineas,
        "costo_materiales_c": costo_materiales_c,
    }
