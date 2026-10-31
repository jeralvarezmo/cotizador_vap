"""Conexión a SQLite (módulo estándar sqlite3, sin ORM)."""
import sqlite3
from pathlib import Path

from flask import current_app, g

CARPETA_SQL = Path(__file__).resolve().parent.parent / "database"


def get_db():
    """Una conexión por petición. row_factory permite leer columnas por nombre."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")  # SQLite no la activa por defecto
    return g.db


def close_db(_error=None):
    conexion = g.pop("db", None)
    if conexion is not None:
        conexion.close()


def init_db(con_demo=True):
    """Crea las tablas y (opcional) carga los datos de demostración."""
    db = get_db()
    db.executescript((CARPETA_SQL / "schema.sql").read_text(encoding="utf-8"))
    if con_demo:
        db.executescript((CARPETA_SQL / "seed_demo.sql").read_text(encoding="utf-8"))
    db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
