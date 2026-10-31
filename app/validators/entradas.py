"""Validación de entradas en el SERVIDOR (nunca se confía solo en el navegador).

Cada validador devuelve (datos, errores). Si 'errores' está vacío, los datos son válidos.
"""
import re
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from ..catalogos import (BASES_MARGEN, CATEGORIAS_MATERIAL, ESTADOS_DATOS,
                         FORMAS, REGLAS, TIPOS_INVENTARIO, UNIDADES)


def _t(form, campo):
    return (form.get(campo) or "").strip()


def a_decimal(texto, nombre):
    """Texto -> Decimal. Acepta coma o punto decimal. Devuelve (valor, error)."""
    t = (texto or "").strip().replace(",", ".")
    if not t:
        return None, f"{nombre}: es obligatorio."
    try:
        v = Decimal(t)
    except InvalidOperation:
        return None, f"{nombre}: debe ser un número (ejemplo: 1.20)."
    if not v.is_finite():  # Decimal acepta 'NaN' e 'Infinity': se rechazan
        return None, f"{nombre}: no es un número válido."
    return v, None


def entero(texto, nombre, minimo, maximo):
    try:
        n = int(str(texto).strip())
    except (TypeError, ValueError):
        return None, f"{nombre}: debe ser un número entero."
    if n < minimo or n > maximo:
        return None, f"{nombre}: debe estar entre {minimo} y {maximo}."
    return n, None


def quetzales_a_centavos(texto, nombre):
    v, e = a_decimal(texto, nombre)
    if e:
        return None, e
    if v < 0:
        return None, f"{nombre}: no puede ser negativo."
    if v > Decimal("10000000"):
        return None, f"{nombre}: es demasiado grande."
    return int((v * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)), None


def validar_medida(texto, nombre, minimo, maximo):
    """Medida en metros: mayor que 0 y dentro de los límites provisionales."""
    v, e = a_decimal(texto, nombre)
    if e:
        return None, e
    if v <= 0:
        return None, f"{nombre}: debe ser mayor que cero."
    if v < minimo or v > maximo:
        return None, f"{nombre}: debe estar entre {minimo} y {maximo} m."
    return v.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP), None


def largo_maximo(texto, maximo, nombre, errores, clave):
    if len(texto) > maximo:
        errores[clave] = f"{nombre}: máximo {maximo} caracteres."


def validar_cliente(form):
    d = {k: _t(form, k) for k in ("nombre", "telefono", "correo", "direccion", "observaciones")}
    e = {}
    if not d["nombre"]:
        e["nombre"] = "El nombre es obligatorio."
    for campo, nombre, maximo in (("nombre", "Nombre", 120), ("direccion", "Dirección", 200),
                                  ("observaciones", "Observaciones", 1000), ("correo", "Correo", 120)):
        largo_maximo(d[campo], maximo, nombre, e, campo)
    if d["telefono"]:
        digitos = re.sub(r"\D", "", d["telefono"])
        if not re.fullmatch(r"[0-9+\-\s()]+", d["telefono"]) or not 7 <= len(digitos) <= 15:
            e["telefono"] = "Teléfono: usa entre 7 y 15 dígitos (puede llevar espacios, + o -)."
    if d["correo"] and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", d["correo"]):
        e["correo"] = "Correo: formato no válido."
    return d, e


def validar_material(form):
    d = {k: _t(form, k) for k in ("nombre", "categoria", "unidad", "caracteristicas", "proveedor", "precio")}
    d["activo"] = 1 if form.get("activo") == "1" else 0
    d["es_demo"] = 1 if form.get("es_demo") == "1" else 0
    e = {}
    if not d["nombre"]:
        e["nombre"] = "El nombre es obligatorio."
    if d["categoria"] not in CATEGORIAS_MATERIAL:
        e["categoria"] = "Elige una categoría."
    if d["unidad"] not in UNIDADES:
        e["unidad"] = "Elige una unidad."
    for campo, nombre, maximo in (("nombre", "Nombre", 120), ("caracteristicas", "Características", 200),
                                  ("proveedor", "Proveedor", 120)):
        largo_maximo(d[campo], maximo, nombre, e, campo)
    centavos, err = quetzales_a_centavos(d["precio"], "Precio")
    if err:
        e["precio"] = err
    else:
        d["precio_centavos"] = centavos
    return d, e


def validar_producto(form):
    d = {k: _t(form, k) for k in ("nombre", "descripcion", "estado_datos")}
    d["activo"] = 1 if form.get("activo") == "1" else 0
    e = {}
    if not d["nombre"]:
        e["nombre"] = "El nombre es obligatorio."
    if d["estado_datos"] not in ESTADOS_DATOS:
        e["estado_datos"] = "Estado de datos no válido."
    largo_maximo(d["nombre"], 120, "Nombre", e, "nombre")
    largo_maximo(d["descripcion"], 500, "Descripción", e, "descripcion")
    return d, e


def validar_componentes(form):
    """Receta editable: listas paralelas comp_id[], comp_etiqueta[], ... Devuelve (lista, errores)."""
    campos = ("comp_id", "comp_etiqueta", "comp_regla", "comp_factor", "comp_desp", "comp_material")
    listas = [form.getlist(c) for c in campos]
    comps, errores = [], []
    for i, (cid, etiqueta, regla, factor, desp, material) in enumerate(zip(*listas), start=1):
        pref = f"Componente {i}: "
        f, ef = a_decimal(factor, "Factor")
        dsp, ed = a_decimal(desp or "0", "Desperdicio")
        if not etiqueta.strip():
            errores.append(pref + "la etiqueta es obligatoria.")
        if regla not in REGLAS:
            errores.append(pref + "regla no válida.")
        if ef or f < 0 or f > 1000:
            errores.append(pref + (ef or "Factor: debe estar entre 0 y 1000."))
        if ed or dsp < 0 or dsp > 100:
            errores.append(pref + (ed or "Desperdicio: debe estar entre 0 y 100 %."))
        mid = int(material) if material.strip().isdigit() else None
        comps.append({"id": int(cid), "etiqueta": etiqueta.strip(), "regla": regla,
                      "factor": float(f) if not ef else 0, "desperdicio_pct": float(dsp) if not ed else 0,
                      "material_id": mid})
    return comps, errores


def _opcional_positivo(form, campo, nombre, errores, maximo=100):
    texto = _t(form, campo)
    if not texto:
        return None
    v, e = a_decimal(texto, nombre)
    if e or v <= 0 or v > maximo:
        errores[campo] = e or f"{nombre}: debe ser mayor que 0 y no más de {maximo}."
        return None
    return float(v)


def validar_inventario(form):
    d = {k: _t(form, k) for k in ("tipo", "forma", "descripcion", "espesor", "serie", "color", "ubicacion", "observaciones")}
    e = {}
    if d["tipo"] not in TIPOS_INVENTARIO:
        e["tipo"] = "Elige existencia o sobrante."
    if d["forma"] not in FORMAS:
        e["forma"] = "Elige la forma."
    if not d["descripcion"]:
        e["descripcion"] = "La descripción es obligatoria."
    for campo in ("descripcion", "espesor", "serie", "color", "ubicacion"):
        largo_maximo(d[campo], 150, campo.capitalize(), e, campo)
    largo_maximo(d["observaciones"], 500, "Observaciones", e, "observaciones")
    cant, err = a_decimal(_t(form, "cantidad") or "1", "Cantidad")
    if err or cant < 0 or cant > 100000:
        e["cantidad"] = err or "Cantidad: debe estar entre 0 y 100000."
    d["cantidad"] = float(cant) if not err else 1
    d["largo_m"] = _opcional_positivo(form, "largo_m", "Largo", e)
    d["ancho_m"] = _opcional_positivo(form, "ancho_m", "Ancho", e)
    d["alto_m"] = _opcional_positivo(form, "alto_m", "Alto", e)
    mid = _t(form, "material_id")
    d["material_id"] = int(mid) if mid.isdigit() else None
    d["reutilizable"] = 1 if form.get("reutilizable") == "1" else 0
    return d, e


def validar_configuracion(form):
    d = {k: _t(form, k) for k in ("nombre_negocio", "ubicacion_negocio", "base_margen", "condiciones")}
    e = {}
    p, err = a_decimal(_t(form, "porcentaje"), "Porcentaje")
    if err or p < 0 or p > 500:
        e["porcentaje"] = err or "Porcentaje: debe estar entre 0 y 500."
    elif d["base_margen"] == "margen_sobre_precio" and p >= 100:
        e["porcentaje"] = "El margen sobre el precio debe ser menor a 100 %."
    if d["base_margen"] not in BASES_MARGEN:
        e["base_margen"] = "Base de cálculo no válida."
    vig, err = entero(_t(form, "vigencia_dias"), "Vigencia", 1, 365)
    if err:
        e["vigencia_dias"] = err
    mn, e1 = a_decimal(_t(form, "medida_min"), "Medida mínima")
    mx, e2 = a_decimal(_t(form, "medida_max"), "Medida máxima")
    if e1 or e2 or mn <= 0 or mx > 100 or mn >= mx:
        e["medida_min"] = e1 or e2 or "Los límites deben cumplir 0 < mínima < máxima ≤ 100 m."
    if not d["nombre_negocio"]:
        e["nombre_negocio"] = "El nombre del negocio es obligatorio."
    largo_maximo(d["condiciones"], 1500, "Condiciones", e, "condiciones")
    if not e:
        d.update(porcentaje=format(p.normalize(), "f"), vigencia_dias=str(vig),
                 medida_min=format(mn.normalize(), "f"), medida_max=format(mx.normalize(), "f"))
    else:
        d.update(porcentaje=_t(form, "porcentaje"), vigencia_dias=_t(form, "vigencia_dias"),
                 medida_min=_t(form, "medida_min"), medida_max=_t(form, "medida_max"))
    return d, e
