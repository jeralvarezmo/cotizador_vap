"""Configuración editable (porcentaje provisional, vigencia, límites, textos)."""


def obtener(db):
    return {r["clave"]: r["valor"] for r in db.execute("SELECT clave, valor FROM configuracion")}


def guardar(db, valores):
    with db:
        for clave, valor in valores.items():
            db.execute("UPDATE configuracion SET valor = ? WHERE clave = ?", (str(valor), clave))
