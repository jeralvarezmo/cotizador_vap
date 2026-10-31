"""Validación de una cotización: cabecera y elementos (sin acceso a la base de datos)."""
from ..catalogos import BASES_MARGEN, CATEGORIAS_PERFIL, ORIGENES_MEDIDA
from .entradas import a_decimal, entero, quetzales_a_centavos, validar_medida


def validar_cabecera(f, cfg, ids_clientes):
    """Devuelve (cab, errores). 'f' es request.form o un dict de textos."""
    errores, cab = [], {}
    cid, e = entero(f.get("cliente_id"), "Cliente", 1, 10**9)
    if e or cid not in ids_clientes:
        errores.append("Selecciona un cliente registrado.")
    cab["cliente_id"] = cid
    vig, e = entero(f.get("vigencia_dias"), "Vigencia (días)", 1, 365)
    if e:
        errores.append(e)
    cab["vigencia_dias"] = vig
    for campo, nombre in (("mano_obra", "Mano de obra"), ("transporte", "Transporte"), ("otros", "Otros conceptos")):
        c, e = quetzales_a_centavos((f.get(campo) or "0").strip() or "0", nombre)
        if e:
            errores.append(e)
        cab[campo + "_c"] = c
    base = f.get("base")
    if base not in BASES_MARGEN:
        errores.append("La base de cálculo del porcentaje no es válida.")
    cab["base"] = base
    pct, e = a_decimal(f.get("porcentaje"), "Porcentaje")
    if e or pct < 0 or pct > 500:
        errores.append(e or "Porcentaje: debe estar entre 0 y 500.")
    elif base == "margen_sobre_precio" and pct >= 100:
        errores.append("El margen sobre el precio debe ser menor a 100 %.")
    cab["porcentaje"] = pct
    for campo, nombre, maximo in (("otros_detalle", "Detalle de otros conceptos", 200),
                                  ("observaciones", "Observaciones", 1000), ("condiciones", "Condiciones", 1500)):
        texto = (f.get(campo) or "").strip()
        if len(texto) > maximo:
            errores.append(f"{nombre}: máximo {maximo} caracteres.")
        cab[campo] = texto
    return cab, errores


def _material_opcional(texto, etiqueta, materiales, categorias, errores, pref):
    texto = (texto or "").strip()
    if not texto:
        return None
    mid, e = entero(texto, etiqueta, 1, 10**9)
    m = materiales.get(mid)
    if e or m is None or not m["activo"] or m["categoria"] not in categorias:
        errores.append(pref + f"el material elegido para «{etiqueta}» no es válido.")
        return None
    return mid


def validar_item(fila, n, productos, materiales, limites):
    """Valida una fila del formulario. Devuelve (item, errores)."""
    pref = f"Elemento {n}: "
    errores = []
    pid, e = entero(fila["producto"], "Producto", 1, 10**9)
    if e or pid not in productos or not productos[pid]["activo"]:
        errores.append(pref + "selecciona un producto válido.")
    ancho, e = validar_medida(fila["ancho"], "Ancho", *limites)
    if e:
        errores.append(pref + e)
    alto, e = validar_medida(fila["alto"], "Alto", *limites)
    if e:
        errores.append(pref + e)
    cantidad, e = entero(fila["cantidad"] or "1", "Cantidad", 1, 999)
    if e:
        errores.append(pref + e)
    hojas, e = entero(fila["hojas"] or "1", "Hojas", 1, 10)
    if e:
        errores.append(pref + e)
    if fila["origen"] not in ORIGENES_MEDIDA:
        errores.append(pref + "origen de la medida no válido.")
    ident, notas = fila["ident"].strip(), fila["notas"].strip()
    if len(ident) > 80:
        errores.append(pref + "la identificación admite máximo 80 caracteres.")
    if len(notas) > 200:
        errores.append(pref + "las características admiten máximo 200 caracteres.")
    perfil = _material_opcional(fila["perfil"], "perfil", materiales, CATEGORIAS_PERFIL, errores, pref)
    vidrio = _material_opcional(fila["vidrio"], "vidrio", materiales, ("vidrio",), errores, pref)
    item = {"ident": ident, "producto_id": pid, "ancho": ancho, "alto": alto, "cantidad": cantidad,
            "hojas": hojas, "origen": fila["origen"], "perfil_id": perfil, "vidrio_id": vidrio, "notas": notas}
    return item, errores
