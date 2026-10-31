# PROGRESO — Cotizador VAP (actualizado al final de la sesión del 2026-10-10)

## Qué funciona (comprobado)
- 39 pruebas automáticas pasan con `pytest` (motor, validadores y recorrido completo con el cliente de pruebas de Flask), en Linux con Python 3.12 y Flask 3.1.
- El servidor real arranca con `python run.py` y responde por HTTP: inicio, clientes, cotización nueva, productos, inventario; se creó un cliente, se guardó una cotización de 2 elementos por POST, se consultó su detalle y su versión imprimible, se aprobó y se comprobó que no puede volver a pendiente.

## Qué NO se ha comprobado
- Visualización en un navegador real (diseño, JavaScript de «Agregar elemento» y filtro de perfiles).
- «Guardar como PDF» desde el navegador (solo se verificó el HTML de impresión).
- Ejecución en Windows y con Visual Studio Code.

## Archivos
Todo el proyecto está creado (ver README.md). Módulos terminados: engine/, validators/, repositories/, services/, routes/, templates/, static/, database/, tests/, scripts/, docs/.

## Pendiente / siguiente paso exacto
1. Abrir la app en el navegador y recorrer el guion del README; anotar fallos visuales o de JavaScript.
2. Levantamiento real del negocio (ver docs/ESTADO_Y_SUPUESTOS.md): recetas, unidades, base del margen, impuestos, segunda variante de ventana.
3. Completar las columnas «Cambios realizados» y «Qué aprendí» de AI_USAGE_LOG.md y empezar la ruta de docs/RUTA_DE_APRENDIZAJE.md.
