# Cotizador VAP — Vidrios y Aluminios Álvarez (PROTOTIPO ACADÉMICO)

Sistema web local de gestión y cotización para un negocio de vidrio, aluminio y PVC.
**Todos los precios, proveedores, recetas y cantidades son DATOS DE DEMOSTRACIÓN — NO UTILIZAR PARA COTIZACIONES REALES.**
Las reglas reales del negocio están pendientes de levantamiento (ver `docs/ESTADO_Y_SUPUESTOS.md`).

Flujo: Cliente → Producto → Medidas → Materiales → Cálculos → Costos → Precio → Cotización → Guardado → Historial → Impresión.

## Cómo ejecutarlo en VS Code

1. Instala **Python 3.10 o superior** (en Windows marca «Add Python to PATH») y **VS Code** con la extensión *Python*.
2. Descomprime el ZIP. En VS Code: **Archivo → Abrir carpeta…** y elige `cotizador-vap`.
3. Abre la terminal de VS Code (**Terminal → Nueva terminal**) y ejecuta:

   **Windows (PowerShell)**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python run.py
   ```
   Si PowerShell bloquea la activación: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` y repite el segundo comando
   (o usa `.venv\Scripts\activate.bat` en una terminal CMD).

   **macOS / Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python3 run.py
   ```
4. Abre **http://127.0.0.1:5000** en el navegador. La primera vez se crea `instance/cotizador.db` con datos de demostración.
5. Si VS Code pide elegir intérprete: `Ctrl+Shift+P` → *Python: Select Interpreter* → el de `.venv`.

Atajo: `scripts/iniciar.bat` (Windows) o `scripts/iniciar.sh` (macOS/Linux) hacen los pasos 3–4.

**Reiniciar datos de demostración:** `python scripts/init_db.py --reiniciar` (borra la BD local).
**Pruebas:** `pip install -r requirements-dev.txt` y luego `pytest`.

## Guion de demostración (≈5 min)
1. *Inicio*: indicadores. 2. *Clientes → Nuevo cliente* (guardar). 3. *Nueva cotización*: elegir cliente; elemento
«Habitación 1: Ventana 1», producto *Ventana corrediza de PVC*, ancho 1.20, alto 1.00, hojas 2; agregar un segundo elemento (puerta).
4. *Calcular (vista previa)*: ver área, perímetro, materiales, cantidades, costos, utilidad y precio. 5. *Guardar*.
6. En *Materiales*, subir el precio del vidrio; volver a la cotización guardada: **no cambia** (snapshot).
7. *Marcar como aprobada* (ya no puede volver a pendiente). 8. *Versión para el cliente / imprimir* → «Guardar como PDF».
9. Mostrar *Productos* (recetas editables) e *Inventario* (registro básico de sobrantes).

## Estructura
```
app/  __init__.py (create_app) · db.py · catalogos.py · filtros.py
      routes/ (HTTP) → services/ (casos de uso) → engine/ (cálculo puro) + validators/ → repositories/ (SQL) → SQLite
      templates/ · static/css · static/js
database/ schema.sql · seed_demo.sql      tests/      scripts/      docs/      AI_USAGE_LOG.md
```
El motor (`app/engine/`) no importa Flask ni SQLite: se puede probar y entender por separado.

## Seguridad básica incluida
Validación en el servidor · SQL parametrizado · escape automático de Jinja · claves foráneas · transacciones ·
sin secretos en el código · versión del cliente sin costos/proveedores/margen · **solo acepta conexiones locales**
(sin login). No hay protección CSRF ni autenticación todavía: **no exponer a internet ni a una red no confiable.**

## Autoría
Este prototipo fue **generado con IA (Claude)** como referencia de aprendizaje. Registro en `AI_USAGE_LOG.md`.
Ruta para reconstruirlo por tu cuenta: `docs/RUTA_DE_APRENDIZAJE.md`.
