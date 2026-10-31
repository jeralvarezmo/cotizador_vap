#!/usr/bin/env sh
# macOS / Linux: crea el entorno la primera vez, instala Flask y arranca la app.
cd "$(dirname "$0")/.." || exit 1
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
echo "Abre http://127.0.0.1:5000 en el navegador (Ctrl+C para detener)."
python run.py
