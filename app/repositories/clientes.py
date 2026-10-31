"""Consultas SQL de clientes (siempre parametrizadas con ?)."""


def listar(db, q=""):
    sql = ("SELECT c.*, (SELECT COUNT(*) FROM cotizaciones x WHERE x.cliente_id = c.id) AS n_cotizaciones "
           "FROM clientes c")
    params = []
    if q:
        sql += " WHERE c.nombre LIKE ? OR c.telefono LIKE ?"
        params = [f"%{q}%", f"%{q}%"]
    return db.execute(sql + " ORDER BY c.nombre COLLATE NOCASE", params).fetchall()


def obtener(db, cid):
    return db.execute("SELECT * FROM clientes WHERE id = ?", (cid,)).fetchone()


def contar(db):
    return db.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]


def crear(db, d):
    with db:
        cur = db.execute(
            "INSERT INTO clientes (nombre, telefono, correo, direccion, observaciones) "
            "VALUES (:nombre, :telefono, :correo, :direccion, :observaciones)", d)
    return cur.lastrowid


def actualizar(db, cid, d):
    with db:
        db.execute(
            "UPDATE clientes SET nombre=:nombre, telefono=:telefono, correo=:correo, direccion=:direccion, "
            "observaciones=:observaciones WHERE id=:id", {**d, "id": cid})
