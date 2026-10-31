# Estado del prototipo y supuestos

Fecha: 2026-10-10. Comprobación hecha por la IA: 39 pruebas automáticas y arranque del servidor en Linux (Python 3.12, Flask 3.1).
**No comprobado:** navegador real, JavaScript, impresión a PDF, Windows.

## Implementado y comprobado (pruebas o HTTP)
| Función | Cómo se comprobó |
|---|---|
| Clientes: alta, lista, búsqueda por nombre/teléfono, ficha, edición, cotizaciones asociadas | pruebas + HTTP |
| Materiales: alta, edición, filtros, activo/inactivo, precio vigente | pruebas |
| Productos: 5 productos de demostración, receta editable | pruebas |
| Geometría (área, perímetro) con validación en servidor | pruebas |
| Motor de cálculo: materiales, cantidades, desperdicio, costo, mano de obra, transporte, otros, recargo/margen, utilidad, precio | pruebas |
| Cotización con varios elementos, guardado, snapshot de precios, número visible, vigencia, historial | pruebas + HTTP |
| Estados Pendiente/Aprobada/Rechazada/Cancelada con transiciones validadas | pruebas |
| Duplicar (mismos importes / recalculando con precios vigentes) | pruebas |
| Versión imprimible sin costos, proveedores, margen ni utilidad | pruebas (HTML) |
| Dashboard con indicadores | página carga |
| Solo conexiones locales (403 desde otra IP) | pruebas |

## Implementado pero SIN comprobar en navegador
JavaScript (agregar/quitar elementos, filtrar perfil según producto, confirmaciones), estilos, «Guardar como PDF».

## Simulado (datos de demostración — no usar en cotizaciones reales)
Precios, proveedores, materiales, recetas (factores, desperdicios, cantidades de accesorios), porcentaje de recargo (30 %), vigencia (15 días), límites de medidas (0.10–10 m), clientes ficticios, sobrantes de ejemplo.

## Parcial
Inventario: registro **manual** de existencias y sobrantes (sin descuentos automáticos, sin edición de registros).

## No implementado (decisión consciente)
Autenticación y roles · protección CSRF · editar una cotización ya guardada (se duplica) · alta de productos/componentes desde la pantalla (se hace por SQL; ver DISENO_TECNICO.md) ·
estados operativos del trabajo · optimización de cortes · descuento automático de existencias · PDF con biblioteca · impuestos · historial de precios por proveedor · fotos y toma de medidas en sitio.

## DATOS PENDIENTES DE CONFIRMAR con el negocio
1. Segunda variante de ventana corrediza (hoy: aluminio como SUPUESTO).
2. Reglas reales de fabricación por producto (perfiles, vidrio, accesorios, desperdicio, descuentos por marco/holgura).
3. Unidad interna definitiva y unidades de compra/corte (hoy: metros; largo de barra, medida de plancha).
4. Base del margen: ¿recargo sobre el costo o margen sobre el precio de venta? Porcentaje real.
5. Impuestos y facturación aplicable (no se calculan).
6. Mano de obra: cómo se cobra (por m², pieza, trabajo, día), transporte e instalación.
7. Tiempo actual por cotización y errores frecuentes (línea base).
8. Campos obligatorios del cliente (hoy: solo el nombre).
9. ¿Una cotización aprobada puede cancelarse? (hoy: sí, supuesto).
10. Rúbrica, fecha de defensa y notación de pseudocódigo del profesor (no disponibles en este proyecto).
