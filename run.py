"""Punto de entrada.  Ejecutar:  python run.py   ->   http://127.0.0.1:5000"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    # 127.0.0.1 = solo esta computadora. La app NO tiene login todavía: no exponerla a la red.
    app.run(host="127.0.0.1", port=5000, debug=True)
