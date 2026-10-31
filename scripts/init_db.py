"""Recrea la base de datos con los datos de demostración.

Uso:  python scripts/init_db.py --reiniciar     (BORRA instance/cotizador.db y la recrea)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app, db  # noqa: E402

app = create_app()
ruta = app.config["DATABASE"]
if "--reiniciar" not in sys.argv:
    print(f"Base de datos actual: {ruta}\nUsa --reiniciar para BORRARLA y recrearla con datos de demostración.")
    sys.exit(0)
os.remove(ruta)
with app.app_context():
    db.init_db()
print("Base de datos recreada con datos de demostración.")
