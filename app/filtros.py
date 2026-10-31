"""Filtros y variables globales de Jinja para las plantillas."""
from datetime import datetime
from decimal import Decimal

from . import catalogos
from .engine.precios import formato_q


def _fecha(iso):
    try:
        return datetime.strptime(str(iso)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return iso or ""


def _cantidad(valor):
    """Número sin ceros sobrantes: 2.5000 -> 2.5 ; 4.0 -> 4."""
    try:
        return format(Decimal(str(valor)).normalize(), "f")
    except Exception:
        return valor


def registrar_filtros(app):
    env = app.jinja_env
    env.filters.update(
        q=formato_q, fecha=_fecha, cant=_cantidad, cot_num=lambda n: f"COT-{int(n):04d}"
    )
    env.globals.update(
        CATEGORIAS_MATERIAL=catalogos.CATEGORIAS_MATERIAL, UNIDADES=catalogos.UNIDADES,
        ESTADOS_DATOS=catalogos.ESTADOS_DATOS, ESTADOS=catalogos.ESTADOS,
        BASES_MARGEN=catalogos.BASES_MARGEN, ORIGENES_MEDIDA=catalogos.ORIGENES_MEDIDA,
        REGLAS=catalogos.REGLAS, TIPOS_INVENTARIO=catalogos.TIPOS_INVENTARIO,
        FORMAS=catalogos.FORMAS, ESTADOS_INVENTARIO=catalogos.ESTADOS_INVENTARIO,
    )
