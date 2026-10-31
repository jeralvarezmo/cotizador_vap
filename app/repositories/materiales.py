"""Consultas SQL de materiales y precios vigentes."""


def listar(db, categoria=None, estado=None, q=None):
    where, params = [], []
    if categoria:
        where.append("categoria = ?")
        params.append(categoria)
    if estado == "activos":
        where.append("activo = 1")
    elif estado == "inactivos":
        where.append("activo = 0")
    if q:
        where.append("(nombre LIKE ? OR proveedor LIKE ? OR caracteristicas LIKE ?)")
        params += [f"%{q}%"] * 3
    sql = "SELECT * FROM materiales" + (" WHERE " + " AND ".join(where) if where else "")
    return db.execute(sql + " ORDER BY categoria, nombre COLLATE NOCASE", params).fetchall()


def obtener(db, mid):
    return db.execute("SELECT * FROM materiales WHERE id = ?", (mid,)).fetchone()


def crear(db, d):
    with db:
        cur = db.execute(
            "INSERT INTO materiales (nombre, categoria, unidad, caracteristicas, proveedor, precio_centavos, activo, es_demo) "
            "VALUES (:nombre, :categoria, :unidad, :caracteristicas, :proveedor, :precio_centavos, :activo, :es_demo)", d)
    return cur.lastrowid


def actualizar(db, mid, d):
    # Cambiar el precio NO altera cotizaciones guardadas: ellas tienen su propio snapshot.
    with db:
        db.execute(
            "UPDATE materiales SET nombre=:nombre, categoria=:categoria, unidad=:unidad, caracteristicas=:caracteristicas, "
            "proveedor=:proveedor, precio_centavos=:precio_centavos, activo=:activo, es_demo=:es_demo, "
            "actualizado_en=datetime('now','localtime') WHERE id=:id", {**d, "id": mid})
