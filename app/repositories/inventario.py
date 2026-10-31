"""Registro básico (manual) de existencias y sobrantes."""


def listar(db, tipo=None, estado=None):
    where, params = [], []
    if tipo:
        where.append("i.tipo = ?")
        params.append(tipo)
    if estado:
        where.append("i.estado = ?")
        params.append(estado)
    sql = ("SELECT i.*, m.nombre AS material_nombre FROM inventario i LEFT JOIN materiales m ON m.id = i.material_id"
           + (" WHERE " + " AND ".join(where) if where else "") + " ORDER BY i.id DESC")
    return db.execute(sql, params).fetchall()


def crear(db, d):
    with db:
        db.execute(
            "INSERT INTO inventario (tipo, material_id, descripcion, forma, cantidad, largo_m, ancho_m, alto_m, espesor, "
            "serie, color, ubicacion, reutilizable, observaciones) VALUES (:tipo, :material_id, :descripcion, :forma, "
            ":cantidad, :largo_m, :ancho_m, :alto_m, :espesor, :serie, :color, :ubicacion, :reutilizable, :observaciones)", d)


def cambiar_estado(db, iid, estado):
    with db:
        db.execute("UPDATE inventario SET estado = ? WHERE id = ?", (estado, iid))
