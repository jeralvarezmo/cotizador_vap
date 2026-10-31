"""Casos de uso de cotizaciones: coordina validadores, engine y repositorios.

Aquí NO hay fórmulas (están en engine/) ni SQL (está en repositories/).
"""
from datetime import date, timedelta
from decimal import Decimal

from ..engine import costos, precios
from ..engine.estados import validar_transicion
from ..repositories import clientes as repo_clientes
from ..repositories import configuracion as repo_cfg
from ..repositories import cotizaciones as repo
from ..repositories import materiales as repo_mat
from ..repositories import productos as repo_prod
from ..validators import cotizacion as val

CAMPOS_FILA = ("ident", "producto", "ancho", "alto", "cantidad", "hojas", "origen", "perfil", "vidrio", "notas")


def fila_vacia():
    return {"ident": "", "producto": "", "ancho": "", "alto": "", "cantidad": "1", "hojas": "2",
            "origen": "tomada", "perfil": "", "vidrio": "", "notas": ""}


def valores_iniciales(cfg):
    return {"cliente_id": "", "vigencia_dias": cfg["vigencia_dias"], "mano_obra": "0", "transporte": "0",
            "otros": "0", "otros_detalle": "", "porcentaje": cfg["porcentaje"], "base": cfg["base_margen"],
            "observaciones": "", "condiciones": cfg["condiciones"]}


def leer_filas(form):
    """Convierte los campos item_*[] del formulario en una lista de filas (dicts de texto)."""
    listas = {c: form.getlist(f"item_{c}") for c in CAMPOS_FILA}
    n = max((len(v) for v in listas.values()), default=0)
    filas = [{c: (listas[c][i] if i < len(listas[c]) else "") for c in CAMPOS_FILA} for i in range(n)]
    vacias = ("cantidad", "hojas", "origen")  # tienen valor por defecto: no cuentan como "llena"
    return [f for f in filas if any(v.strip() for k, v in f.items() if k not in vacias)]


def _elegir_material(comp, item, materiales):
    elegido = item["perfil_id"] if comp["rol"] == "perfil" else item["vidrio_id"] if comp["rol"] == "vidrio" else None
    mid = elegido or comp["material_id"]
    m = materiales.get(mid)
    if m is None or not m["activo"]:
        raise ValueError(f"No hay un material activo para «{comp['etiqueta']}». Elige uno o edita la receta.")
    if elegido and m["categoria"] not in comp["categorias_permitidas"].split(","):
        raise ValueError(f"El material elegido no sirve para «{comp['etiqueta']}» de este producto.")
    return m


def _armar_componentes(db, producto_id, item, materiales):
    comps = []
    for c in repo_prod.componentes(db, producto_id):
        c = dict(c)
        comps.append({"etiqueta": c["etiqueta"], "rol": c["rol"], "regla": c["regla"], "factor": c["factor"],
                      "desperdicio_pct": c["desperdicio_pct"], "material": _elegir_material(c, item, materiales)})
    if not comps:
        raise ValueError("el producto no tiene componentes en su receta.")
    return comps


def totalizar(items, cab):
    costo_mat = sum(i["costo_materiales_c"] for i in items)
    costo_total = costo_mat + cab["mano_obra_c"] + cab["transporte_c"] + cab["otros_c"]
    p = precios.calcular_precio(costo_total, cab["porcentaje"], cab["base"])
    # El precio ofertado se reparte entre los elementos según su costo de materiales.
    for it, parte in zip(items, precios.repartir_proporcional(p["precio_c"], [i["costo_materiales_c"] for i in items])):
        it["precio_c"] = parte
    return {"costo_materiales_c": costo_mat, "costo_total_c": costo_total, **p,
            "usa_demo": any(ln["es_demo"] for i in items for ln in i["lineas"])}


def preparar(db, cab_form, filas):
    """Valida todo y calcula. Devuelve un dict con errores, elementos y totales (sin guardar)."""
    cfg = repo_cfg.obtener(db)
    limites = (Decimal(cfg["medida_min"]), Decimal(cfg["medida_max"]))
    productos = {p["id"]: dict(p) for p in repo_prod.listar(db)}
    materiales = {m["id"]: dict(m) for m in repo_mat.listar(db)}
    cab, errores = val.validar_cabecera(cab_form, cfg, {c["id"] for c in repo_clientes.listar(db)})
    if not filas:
        errores.append("Agrega al menos un elemento a la cotización.")
    items = []
    for n, fila in enumerate(filas, start=1):
        item, errs = val.validar_item(fila, n, productos, materiales, limites)
        errores += errs
        if errs:
            continue
        try:
            comps = _armar_componentes(db, item["producto_id"], item, materiales)
        except ValueError as e:
            errores.append(f"Elemento {n}: {e}")
            continue
        item.update(costos.calcular_item(comps, item["ancho"], item["alto"], item["cantidad"], item["hojas"]))
        p = productos[item["producto_id"]]
        item.update(producto_nombre=p["nombre"], producto_estado_datos=p["estado_datos"])
        items.append(item)
    res = {"cab": cab, "valores": cab_form, "filas": filas, "errores": errores, "items": items, "totales": None,
           "resumen": None}
    if not errores:
        t = totalizar(items, cab)
        res["totales"] = t
        res["resumen"] = {"costo_materiales_c": t["costo_materiales_c"], "mano_obra_c": cab["mano_obra_c"],
                          "transporte_c": cab["transporte_c"], "otros_c": cab["otros_c"],
                          "otros_detalle": cab["otros_detalle"], "costo_total_c": t["costo_total_c"],
                          "base_margen": cab["base"], "porcentaje": cab["porcentaje"],
                          "utilidad_c": t["utilidad_c"], "precio_total_c": t["precio_c"],
                          "utilidad_sobre_costo": t["utilidad_sobre_costo"],
                          "utilidad_sobre_precio": t["utilidad_sobre_precio"]}
    return res


def guardar(db, res, nota=""):
    cab, t = res["cab"], res["totales"]
    hoy = date.today()
    c = {"fecha": hoy.isoformat(), "cliente_id": cab["cliente_id"], "estado": "pendiente",
         "vigencia_dias": cab["vigencia_dias"], "vigencia_hasta": (hoy + timedelta(days=cab["vigencia_dias"])).isoformat(),
         "observaciones": cab["observaciones"], "condiciones": cab["condiciones"],
         "costo_materiales_c": t["costo_materiales_c"], "mano_obra_c": cab["mano_obra_c"],
         "transporte_c": cab["transporte_c"], "otros_c": cab["otros_c"], "otros_detalle": cab["otros_detalle"],
         "costo_total_c": t["costo_total_c"], "base_margen": cab["base"], "porcentaje": float(cab["porcentaje"]),
         "utilidad_c": t["utilidad_c"], "precio_total_c": t["precio_c"], "usa_demo": 1 if t["usa_demo"] else 0}
    return repo.crear(db, c, res["items"], nota)


def cambiar_estado(db, cid, nuevo, nota=""):
    cot = repo.obtener(db, cid)
    if cot is None:
        raise LookupError("La cotización no existe.")
    validar_transicion(cot["estado"], nuevo)
    repo.cambiar_estado(db, cid, nuevo, nota)


def duplicar(db, cid, recalcular):
    """Duplica una cotización. Con recalcular=True usa los precios VIGENTES; si no, los mismos importes."""
    o = repo.obtener(db, cid)
    if o is None:
        raise LookupError("La cotización no existe.")
    if not recalcular:
        return repo.duplicar_exacto(db, cid)
    cab_form = {"cliente_id": str(o["cliente_id"]), "vigencia_dias": str(o["vigencia_dias"]),
                "mano_obra": f"{o['mano_obra_c'] / 100:.2f}", "transporte": f"{o['transporte_c'] / 100:.2f}",
                "otros": f"{o['otros_c'] / 100:.2f}", "otros_detalle": o["otros_detalle"] or "",
                "porcentaje": str(o["porcentaje"]), "base": o["base_margen"],
                "observaciones": o["observaciones"] or "", "condiciones": o["condiciones"] or ""}
    filas = [{"ident": i["ident"], "producto": str(i["producto_id"]), "ancho": str(i["ancho"]), "alto": str(i["alto"]),
              "cantidad": str(i["cantidad"]), "hojas": str(i["hojas"]), "origen": i["origen"],
              "perfil": str(i["perfil_id"] or ""), "vidrio": str(i["vidrio_id"] or ""), "notas": i["notas"]}
             for i in repo.items(db, cid)]
    res = preparar(db, cab_form, filas)
    if res["errores"]:
        raise ValueError("No se pudo recalcular: " + " ".join(res["errores"]))
    return guardar(db, res, f"Duplicada de COT-{o['numero']:04d} (recalculada con precios vigentes)")
