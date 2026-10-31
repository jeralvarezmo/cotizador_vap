"""Pruebas de validación de entradas (servidor)."""
from decimal import Decimal

import pytest

from app.validators import entradas as v


@pytest.mark.parametrize("texto", ["0", "-1", "abc", "", "NaN", "Infinity", "11", "0.05"])
def test_medidas_invalidas(texto):
    valor, error = v.validar_medida(texto, "Ancho", Decimal("0.10"), Decimal("10"))
    assert valor is None and error


@pytest.mark.parametrize("texto,esperado", [("1.2", "1.200"), ("1,20", "1.200"), (" 0.9 ", "0.900")])
def test_medidas_validas(texto, esperado):
    valor, error = v.validar_medida(texto, "Ancho", Decimal("0.10"), Decimal("10"))
    assert error is None and str(valor) == esperado


def test_quetzales_a_centavos():
    assert v.quetzales_a_centavos("45.50", "Precio") == (4550, None)
    assert v.quetzales_a_centavos("-1", "Precio")[0] is None


def test_cliente_nombre_obligatorio_y_telefono():
    _, e = v.validar_cliente({"nombre": "", "telefono": "12"})
    assert "nombre" in e and "telefono" in e
    datos, e = v.validar_cliente({"nombre": "Ana", "telefono": "5555-0001"})
    assert not e and datos["nombre"] == "Ana"
