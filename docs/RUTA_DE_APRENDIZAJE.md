# Ruta de aprendizaje y reconstrucción (por módulos)

Objetivo: construir **tu propia versión** entendiendo cada archivo. Este prototipo es la referencia, generada con IA (ver `AI_USAGE_LOG.md`).

## Reglas para no confundir código de IA con código tuyo
1. Primero intenta escribir la función tú, **sin mirar** el archivo de referencia; luego compara.
2. Un commit de Git por módulo; mensajes que empiecen con `[propio]`, `[IA]` o `[propio+IA]`.
3. Después de cada módulo, completa una entrada en `AI_USAGE_LOG.md` (qué pediste, qué cambiaste, qué aprendiste).
4. Si no puedes explicar una función sin mirarla, todavía no es tuya: repásala.

## Módulos (en orden)
| # | Módulo | Lee | Aprende | Escribe tú | Pruébalo |
|---|---|---|---|---|---|
| 0 | Preparación | `README.md` | venv, `pip`, Git básico, ejecutar la app | repositorio propio con `.gitignore` | abrir http://127.0.0.1:5000 |
| 1 | Funciones puras | `engine/geometria.py` | `def`, parámetros, `return`, `Decimal` | `calcular_area`, `calcular_perimetro` | `tests/test_engine.py` |
| 2 | Listas y diccionarios | `engine/costos.py` | dicts de recetas, `for`, listas de dicts | `calcular_item` con 2 componentes | caso: 1.2 × 1.0 m, +10 % → 1.32 m² |
| 3 | Dinero y precio | `engine/precios.py` | centavos enteros, redondeo, recargo vs margen | `calcular_precio` (ambas bases) | costo Q1,850 y 30 % → Q2,405.00 / Q2,642.86 |
| 4 | Excepciones y validación | `validators/entradas.py` | `try/except`, `raise`, `Decimal`, rechazar `NaN` | `validar_medida` | valores 0, -1, "abc", "NaN" |
| 5 | SQL y sqlite3 | `database/schema.sql`, `repositories/clientes.py` | tablas, claves, `SELECT/INSERT/UPDATE`, `?` | tabla `clientes` y su repositorio | consola SQLite o pytest |
| 6 | Flask básico | `app/__init__.py`, `routes/clientes.py`, `templates/clientes/` | ruta, request, response, Jinja, POST→redirect | CRUD de clientes | navegador |
| 7 | Servicio de cotización | `services/cotizaciones.py`, `repositories/cotizaciones.py` | transacción, snapshot, capas | guardar una cotización de 1 elemento | `tests/test_app.py` |
| 8 | Estados | `engine/estados.py` | diccionario de transiciones | `validar_transicion` | aprobada → pendiente debe fallar |
| 9 | Impresión | `templates/cotizaciones/imprimir.html`, `print.css` | HTML/CSS, `@media print` | tu versión del documento | Guardar como PDF |
| 10 | Pruebas y defensa | `tests/` | pytest, casos límite | 3 pruebas nuevas | `pytest` |

Antes de cada módulo, pídele a la IA la mini-clase: qué es, para qué sirve, por qué se usa, cómo funciona, dónde está en el proyecto.

## Preguntas de defensa que ya puedes practicar
¿Por qué dinero en centavos? · ¿Qué es el snapshot y por qué existe? · ¿Por qué el motor no importa Flask? · ¿Qué diferencia hay entre recargo y margen? ·
¿Cómo se evita SQL injection? · ¿Qué pasa si falla un guardado a la mitad? · ¿Qué datos son de demostración y cuáles reales? · ¿Qué parte escribiste tú y cómo usaste IA?
