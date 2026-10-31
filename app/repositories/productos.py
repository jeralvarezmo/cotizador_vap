"""Consultas SQL de productos y sus recetas (componentes)."""


def listar(db, solo_activos=False):
    sql = "SELECT * FROM productos" + (" WHERE activo = 1" if solo_activos else "")
    return db.execute(sql + " ORDER BY id").fetchall()


def obtener(db, pid):
    return db.execute("SELECT * FROM productos WHERE id = ?", (pid,)).fetchone()


def componentes(db, pid):
    return db.execute(
        "SELECT c.*, m.nombre AS material_nombre FROM producto_componentes c "
        "LEFT JOIN materiales m ON m.id = c.material_id WHERE c.producto_id = ? ORDER BY c.orden, c.id", (pid,)
    ).fetchall()


def categorias_perfil(db):
    """{producto_id: 'perfil_pvc,perfil_aluminio'} para filtrar el selector de perfil."""
    res = {}
    for r in db.execute("SELECT producto_id, categorias_permitidas FROM producto_componentes WHERE rol = 'perfil'"):
        res.setdefault(r["producto_id"], set()).update(r["categorias_permitidas"].split(","))
    return {k: ",".join(sorted(v)) for k, v in res.items()}


def actualizar(db, pid, d, comps):
    with db:
        db.execute("UPDATE productos SET nombre=:nombre, descripcion=:descripcion, estado_datos=:estado_datos, "
                   "activo=:activo WHERE id=:id", {**d, "id": pid})
        for c in comps:
            db.execute("UPDATE producto_componentes SET etiqueta=:etiqueta, regla=:regla, factor=:factor, "
                       "desperdicio_pct=:desperdicio_pct, material_id=:material_id "
                       "WHERE id=:id AND producto_id=:pid", {**c, "pid": pid})
