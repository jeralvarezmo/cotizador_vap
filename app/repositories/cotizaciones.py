"""Consultas SQL de cotizaciones, elementos, snapshot de precios e historial."""
from datetime import date, timedelta


def contar_por_estado(db):
    return {r["estado"]: r["n"] for r in db.execute("SELECT estado, COUNT(*) AS n FROM cotizaciones GROUP BY estado")}


def listar(db, estado=None, q=None, cliente_id=None, limite=None):
    where, params = [], []
    if estado:
        where.append("c.estado = ?")
        params.append(estado)
    if cliente_id:
        where.append("c.cliente_id = ?")
        params.append(cliente_id)
    if q:
        where.append("(cl.nombre LIKE ? OR c.numero = ?)")
        params += [f"%{q}%", int(q) if q.isdigit() else -1]
    sql = ("SELECT c.*, cl.nombre AS cliente_nombre FROM cotizaciones c JOIN clientes cl ON cl.id = c.cliente_id"
           + (" WHERE " + " AND ".join(where) if where else "") + " ORDER BY c.numero DESC")
    if limite:
        sql += f" LIMIT {int(limite)}"
    return db.execute(sql, params).fetchall()


def obtener(db, cid):
    return db.execute(
        "SELECT c.*, cl.nombre AS cliente_nombre, cl.telefono AS cliente_telefono, cl.correo AS cliente_correo, "
        "cl.direccion AS cliente_direccion FROM cotizaciones c JOIN clientes cl ON cl.id = c.cliente_id WHERE c.id = ?",
        (cid,)).fetchone()


def items(db, cid):
    """Elementos con su detalle, con las mismas claves que produce el engine."""
    res = []
    for r in db.execute("SELECT * FROM cotizacion_items WHERE cotizacion_id = ? ORDER BY orden", (cid,)):
        lineas = [dict(x) for x in db.execute("SELECT * FROM cotizacion_detalle WHERE item_id = ? ORDER BY id", (r["id"],))]
        res.append({
            "ident": r["identificacion"] or "", "producto_id": r["producto_id"], "producto_nombre": r["producto_nombre"],
            "producto_estado_datos": r["producto_estado_datos"], "ancho": r["ancho_m"], "alto": r["alto_m"],
            "origen": r["origen_medida"], "cantidad": r["cantidad"], "hojas": r["hojas"], "perfil_id": r["perfil_id"],
            "vidrio_id": r["vidrio_id"], "notas": r["notas"] or "", "area": r["area_m2"], "perimetro": r["perimetro_m"],
            "costo_materiales_c": r["costo_materiales_c"], "precio_c": r["precio_c"], "lineas": lineas})
    return res


def historial(db, cid):
    return db.execute("SELECT * FROM cotizacion_historial WHERE cotizacion_id = ? ORDER BY id", (cid,)).fetchall()


def crear(db, c, items_, nota=""):
    """Guarda cabecera, elementos y snapshot en UNA transacción (todo o nada)."""
    with db:
        numero = db.execute("SELECT COALESCE(MAX(numero), 0) + 1 FROM cotizaciones").fetchone()[0]
        cur = db.execute(
            "INSERT INTO cotizaciones (numero, fecha, cliente_id, estado, vigencia_dias, vigencia_hasta, observaciones, "
            "condiciones, costo_materiales_c, mano_obra_c, transporte_c, otros_c, otros_detalle, costo_total_c, "
            "base_margen, porcentaje, utilidad_c, precio_total_c, usa_demo) VALUES (:numero, :fecha, :cliente_id, "
            ":estado, :vigencia_dias, :vigencia_hasta, :observaciones, :condiciones, :costo_materiales_c, :mano_obra_c, "
            ":transporte_c, :otros_c, :otros_detalle, :costo_total_c, :base_margen, :porcentaje, :utilidad_c, "
            ":precio_total_c, :usa_demo)", {**c, "numero": numero})
        cid = cur.lastrowid
        for orden, it in enumerate(items_, start=1):
            cur = db.execute(
                "INSERT INTO cotizacion_items (cotizacion_id, orden, identificacion, producto_id, producto_nombre, "
                "producto_estado_datos, ancho_m, alto_m, origen_medida, cantidad, hojas, perfil_id, vidrio_id, notas, "
                "area_m2, perimetro_m, costo_materiales_c, precio_c) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (cid, orden, it["ident"], it["producto_id"], it["producto_nombre"], it["producto_estado_datos"],
                 float(it["ancho"]), float(it["alto"]), it["origen"], it["cantidad"], it["hojas"], it["perfil_id"],
                 it["vidrio_id"], it["notas"], float(it["area"]), float(it["perimetro"]),
                 it["costo_materiales_c"], it["precio_c"]))
            iid = cur.lastrowid
            for ln in it["lineas"]:
                db.execute(
                    "INSERT INTO cotizacion_detalle (item_id, concepto, rol, material_id, material_nombre, unidad, "
                    "cantidad, precio_unit_c, subtotal_c, es_demo, regla_texto) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (iid, ln["concepto"], ln["rol"], ln["material_id"], ln["material_nombre"], ln["unidad"],
                     float(ln["cantidad"]), ln["precio_unit_c"], ln["subtotal_c"], ln["es_demo"], ln["regla_texto"]))
        db.execute("INSERT INTO cotizacion_historial (cotizacion_id, accion, estado_nuevo, nota) VALUES (?,?,?,?)",
                   (cid, "creada", c["estado"], nota))
    return cid


def cambiar_estado(db, cid, nuevo, nota=""):
    with db:
        actual = db.execute("SELECT estado FROM cotizaciones WHERE id = ?", (cid,)).fetchone()["estado"]
        db.execute("UPDATE cotizaciones SET estado = ?, actualizado_en = datetime('now','localtime') WHERE id = ?",
                   (nuevo, cid))
        db.execute("INSERT INTO cotizacion_historial (cotizacion_id, accion, estado_anterior, estado_nuevo, nota) "
                   "VALUES (?,?,?,?,?)", (cid, "estado", actual, nuevo, nota))


def duplicar_exacto(db, cid):
    """Copia la cotización con los MISMOS importes (snapshot), como nueva y pendiente."""
    o = obtener(db, cid)
    hoy = date.today()
    c = {k: o[k] for k in ("cliente_id", "vigencia_dias", "observaciones", "condiciones", "costo_materiales_c",
                           "mano_obra_c", "transporte_c", "otros_c", "otros_detalle", "costo_total_c", "base_margen",
                           "porcentaje", "utilidad_c", "precio_total_c", "usa_demo")}
    c.update(fecha=hoy.isoformat(), estado="pendiente",
             vigencia_hasta=(hoy + timedelta(days=o["vigencia_dias"])).isoformat())
    return crear(db, c, items(db, cid), f"Duplicada de COT-{o['numero']:04d} (mismos importes)")
