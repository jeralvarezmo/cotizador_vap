@echo off
REM Doble clic en Windows: crea el entorno la primera vez, instala Flask y arranca la app.
cd /d "%~dp0\.."
if not exist .venv ( python -m venv .venv )
call .venv\Scripts\activate.bat
pip install -r requirements.txt
echo.
echo Abre http://127.0.0.1:5000 en el navegador (Ctrl+C para detener).
python run.py
