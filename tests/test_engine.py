"""Pruebas del motor de cálculo (puro: sin Flask ni base de datos)."""
from decimal import Decimal

import pytest

from app.engine import costos, estados, geometria, precios


def test_area_y_perimetro():
    assert geometria.calcular_area(Decimal("1.2"), Decimal("1.0")) == Decimal("1.2000")
    assert geometria.calcular_perimetro(Decimal("1.2"), Decimal("1.0")) == Decimal("4.4000")


def test_formato_dinero():
    assert precios.formato_q(185000) == "Q1,850.00"
    assert precios.formato_q(5) == "Q0.05"


def test_recargo_y_margen_son_distintos():
    # Costo Q1,850 y 30 %: el recargo sobre costo NO es el margen sobre precio.
    recargo = precios.calcular_precio(185000, 30, precios.BASE_RECARGO)
    margen = precios.calcular_precio(185000, 30, precios.BASE_MARGEN)
    assert recargo["precio_c"] == 240500          # Q2,405.00
    assert margen["precio_c"] == 264286           # Q2,642.86
    assert recargo["utilidad_c"] == 55500
    assert margen["utilidad_sobre_precio"] == Decimal("30.0")


def test_margen_100_o_mas_se_rechaza():
    with pytest.raises(ValueError):
        precios.calcular_precio(1000, 100, precios.BASE_MARGEN)


def test_repartir_proporcional_suma_exacta():
    partes = precios.repartir_proporcional(10001, [333, 333, 334])
    assert sum(partes) == 10001
    assert precios.repartir_proporcional(100, [0, 0, 0]) == [33, 33, 34]


def _comp(regla, factor, desp, precio, unidad="m2"):
    return {"etiqueta": "X", "rol": "otro", "regla": regla, "factor": factor, "desperdicio_pct": desp,
            "material": {"id": 1, "nombre": "M", "unidad": unidad, "precio_centavos": precio, "es_demo": 1}}


def test_calcular_item_vidrio_con_desperdicio():
    # 1.2 m x 1.0 m = 1.2 m²; +10 % = 1.32 m²; x Q100.00/m² = Q132.00
    r = costos.calcular_item([_comp("area", 1.0, 10, 10000)], Decimal("1.2"), Decimal("1.0"), 1, 1)
    assert r["lineas"][0]["cantidad"] == Decimal("1.3200")
    assert r["costo_materiales_c"] == 13200


def test_calcular_item_multiplica_por_cantidad_y_hojas():
    comps = [_comp("por_hoja", 2, 0, 1800, "unidad"), _comp("fijo", 1, 0, 3500, "unidad")]
    r = costos.calcular_item(comps, Decimal("1"), Decimal("1"), 3, 2)
    # rodamientos: 2 por hoja x 2 hojas x 3 unidades = 12 x Q18 = Q216 ; cerradura: 3 x Q35 = Q105
    assert r["costo_materiales_c"] == 12 * 1800 + 3 * 3500


def test_regla_desconocida():
    with pytest.raises(ValueError):
        costos.calcular_item([_comp("magia", 1, 0, 100)], Decimal("1"), Decimal("1"), 1, 1)


def test_transiciones_de_estado():
    estados.validar_transicion("pendiente", "aprobada")
    with pytest.raises(ValueError):
        estados.validar_transicion("aprobada", "pendiente")
    with pytest.raises(ValueError):
        estados.validar_transicion("rechazada", "aprobada")
