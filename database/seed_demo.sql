-- DATOS DE DEMOSTRACIÓN — NO UTILIZAR PARA COTIZACIONES REALES
-- Precios, proveedores, cantidades y recetas son FICTICIOS. Las reglas reales del
-- negocio están PENDIENTES DE CONFIRMAR mediante el levantamiento con el experto.

INSERT INTO configuracion (clave, valor, descripcion) VALUES
 ('nombre_negocio',    'VIDRIOS Y ALUMINIOS ÁLVAREZ', 'Nombre que aparece en la cotización impresa'),
 ('ubicacion_negocio', 'Salamá, Baja Verapaz, Guatemala', 'Ubicación que aparece en la cotización impresa'),
 ('porcentaje',        '30', 'DATO DE DEMOSTRACIÓN: porcentaje provisional. PENDIENTE DE CONFIRMAR'),
 ('base_margen',       'recargo_sobre_costo', 'PENDIENTE DE CONFIRMAR: recargo sobre el costo o margen sobre el precio'),
 ('vigencia_dias',     '15', 'Vigencia por defecto, en días (demostración)'),
 ('medida_min',        '0.10', 'Límite provisional de validación, en metros'),
 ('medida_max',        '10', 'Límite provisional de validación, en metros'),
 ('condiciones',       'Cotización sujeta a verificación de medidas en el lugar. Forma de pago, anticipo y tiempo de entrega: por acordar. Impuestos: por definir.', 'Condiciones por defecto (editables en cada cotización)');

INSERT INTO clientes (id, nombre, telefono, correo, direccion, observaciones) VALUES
 (1, 'Cliente de ejemplo 1 (FICTICIO)', '5555-0001', NULL, 'Dirección ficticia 1', 'DATO DE DEMOSTRACIÓN'),
 (2, 'Cliente de ejemplo 2 (FICTICIO)', '5555-0002', 'ejemplo@correo.invalid', 'Dirección ficticia 2', 'DATO DE DEMOSTRACIÓN');

INSERT INTO materiales (id, nombre, categoria, unidad, caracteristicas, proveedor, precio_centavos, activo, es_demo) VALUES
 (1,  'Vidrio claro 4 mm (DEMO)',          'vidrio',          'm2',      '4 mm · claro',     'Proveedor Demo A',  9500, 1, 1),
 (2,  'Vidrio claro 6 mm (DEMO)',          'vidrio',          'm2',      '6 mm · claro',     'Proveedor Demo A', 12500, 1, 1),
 (3,  'Vidrio templado 6 mm (DEMO)',       'vidrio',          'm2',      '6 mm · templado',  'Proveedor Demo B', 21000, 1, 1),
 (4,  'Vidrio reflectivo 6 mm (DEMO)',     'vidrio',          'm2',      '6 mm · reflectivo','Proveedor Demo B', 18000, 1, 1),
 (5,  'Perfil de PVC blanco (DEMO)',       'perfil_pvc',      'ml',      'Color blanco',     'Proveedor Demo C',  4200, 1, 1),
 (6,  'Perfil de PVC color madera (DEMO)', 'perfil_pvc',      'ml',      'Color madera',     'Proveedor Demo C',  5200, 1, 1),
 (7,  'Perfil de aluminio natural (DEMO)', 'perfil_aluminio', 'ml',      'Acabado natural',  'Proveedor Demo D',  3800, 1, 1),
 (8,  'Perfil de aluminio bronce (DEMO)',  'perfil_aluminio', 'ml',      'Acabado bronce',   'Proveedor Demo D',  4300, 1, 1),
 (9,  'Tubo de aluminio tubular (DEMO)',   'perfil_aluminio', 'ml',      'Tubular',          'Proveedor Demo D',  3500, 1, 1),
 (10, 'Rodamiento para hoja corrediza (DEMO)', 'rodamiento',  'unidad',  NULL,               'Proveedor Demo E',  1800, 1, 1),
 (11, 'Cerradura / seguro (DEMO)',         'cerradura',       'unidad',  NULL,               'Proveedor Demo E',  3500, 1, 1),
 (12, 'Silicón en tubo (DEMO)',            'silicon',         'tubo',    NULL,               'Proveedor Demo E',  4500, 1, 1),
 (13, 'Tornillería, juego (DEMO)',         'tornillo',        'juego',   NULL,               'Proveedor Demo E',  1200, 1, 1),
 (14, 'Empaque / burlete (DEMO)',          'empaque',         'ml',      NULL,               'Proveedor Demo E',   600, 1, 1),
 (15, 'Bisagra (DEMO)',                    'herraje',         'unidad',  NULL,               'Proveedor Demo E',  2500, 1, 1),
 (16, 'Manija (DEMO)',                     'herraje',         'unidad',  NULL,               'Proveedor Demo E',  2800, 1, 1);

INSERT INTO productos (id, codigo, nombre, categoria, descripcion, estado_datos) VALUES
 (1, 'VCP', 'Ventana corrediza de PVC', 'ventana',
     'Receta de DEMOSTRACIÓN editable. Cantidades y factores ficticios.', 'demostracion'),
 (2, 'VCA', 'Ventana corrediza de aluminio (variante 2)', 'ventana',
     'SUPUESTO DE DEMOSTRACIÓN — PENDIENTE DE CONFIRMAR: la segunda variante exacta no está definida.', 'supuesto'),
 (3, 'PAB', 'Puerta abatible (aluminio o PVC)', 'puerta',
     'Receta de DEMOSTRACIÓN editable. El perfil (aluminio o PVC) se elige al cotizar.', 'demostracion'),
 (4, 'VIT', 'Vitrina de aluminio tubular', 'vitrina',
     'Receta de DEMOSTRACIÓN editable. Cantidades y factores ficticios.', 'demostracion'),
 (5, 'VMD', 'Vidrio a medida', 'vidrio',
     'Solo vidrio: tipo y espesor se eligen al cotizar. Precio por m² de DEMOSTRACIÓN.', 'demostracion');

INSERT INTO producto_componentes
 (producto_id, etiqueta, rol, categorias_permitidas, material_id, regla, factor, desperdicio_pct, orden) VALUES
 -- 1. Ventana corrediza de PVC
 (1, 'Perfil de PVC (marco y hojas)', 'perfil', 'perfil_pvc',      5,  'perimetro', 2.0,  8,  1),
 (1, 'Vidrio',                        'vidrio', 'vidrio',          2,  'area',      1.0, 10,  2),
 (1, 'Rodamientos',                   'otro',   'rodamiento',      10, 'por_hoja',  2,    0,  3),
 (1, 'Cerradura / seguro',            'otro',   'cerradura',       11, 'fijo',      1,    0,  4),
 (1, 'Empaque / burlete',             'otro',   'empaque',         14, 'perimetro', 2.0,  5,  5),
 (1, 'Silicón',                       'otro',   'silicon',         12, 'perimetro', 0.05, 0,  6),
 (1, 'Tornillería',                   'otro',   'tornillo',        13, 'fijo',      1,    0,  7),
 -- 2. Ventana corrediza de aluminio (supuesto)
 (2, 'Perfil de aluminio (marco y hojas)', 'perfil', 'perfil_aluminio', 7, 'perimetro', 2.0, 8, 1),
 (2, 'Vidrio',                        'vidrio', 'vidrio',          2,  'area',      1.0, 10,  2),
 (2, 'Rodamientos',                   'otro',   'rodamiento',      10, 'por_hoja',  2,    0,  3),
 (2, 'Cerradura / seguro',            'otro',   'cerradura',       11, 'fijo',      1,    0,  4),
 (2, 'Empaque / burlete',             'otro',   'empaque',         14, 'perimetro', 2.0,  5,  5),
 (2, 'Silicón',                       'otro',   'silicon',         12, 'perimetro', 0.05, 0,  6),
 (2, 'Tornillería',                   'otro',   'tornillo',        13, 'fijo',      1,    0,  7),
 -- 3. Puerta abatible (perfil de aluminio o PVC)
 (3, 'Perfil (marco y hoja)',         'perfil', 'perfil_aluminio,perfil_pvc', 7, 'perimetro', 2.2, 8, 1),
 (3, 'Vidrio',                        'vidrio', 'vidrio',          3,  'area',      1.0, 10,  2),
 (3, 'Bisagras',                      'otro',   'herraje',         15, 'fijo',      3,    0,  3),
 (3, 'Manija',                        'otro',   'herraje',         16, 'fijo',      1,    0,  4),
 (3, 'Cerradura / seguro',            'otro',   'cerradura',       11, 'fijo',      1,    0,  5),
 (3, 'Empaque / burlete',             'otro',   'empaque',         14, 'perimetro', 1.0,  5,  6),
 (3, 'Silicón',                       'otro',   'silicon',         12, 'perimetro', 0.05, 0,  7),
 (3, 'Tornillería',                   'otro',   'tornillo',        13, 'fijo',      1,    0,  8),
 -- 4. Vitrina de aluminio tubular
 (4, 'Tubo de aluminio (marco)',      'perfil', 'perfil_aluminio', 9,  'perimetro', 1.0,  8,  1),
 (4, 'Tubo de aluminio (travesaños)', 'perfil', 'perfil_aluminio', 9,  'ancho',     2.0,  8,  2),
 (4, 'Vidrio',                        'vidrio', 'vidrio',          1,  'area',      1.0, 10,  3),
 (4, 'Cerradura / seguro',            'otro',   'cerradura',       11, 'fijo',      1,    0,  4),
 (4, 'Silicón',                       'otro',   'silicon',         12, 'perimetro', 0.05, 0,  5),
 (4, 'Tornillería',                   'otro',   'tornillo',        13, 'fijo',      1,    0,  6),
 -- 5. Vidrio a medida
 (5, 'Vidrio',                        'vidrio', 'vidrio',          2,  'area',      1.0, 10,  1);

INSERT INTO inventario
 (tipo, material_id, descripcion, forma, cantidad, largo_m, ancho_m, alto_m, espesor, serie, color, ubicacion, estado, reutilizable, observaciones) VALUES
 ('sobrante',   2,  'Sobrante de vidrio claro 6 mm (DEMO)',          'plana',    1, NULL, 0.45, 0.60, '6 mm', NULL,         'claro',   'Bodega, rincón A (demo)',  'disponible', 1, 'DATO DE DEMOSTRACIÓN'),
 ('sobrante',   7,  'Sobrante de perfil de aluminio natural (DEMO)', 'lineal',   1, 1.35, NULL, NULL, NULL,   'Serie demo', 'natural', 'Bodega, estante 1 (demo)', 'disponible', 1, 'DATO DE DEMOSTRACIÓN'),
 ('existencia', 12, 'Silicón en tubo, existencia (DEMO)',            'unidades', 6, NULL, NULL, NULL, NULL,   NULL,         NULL,      'Bodega (demo)',            'disponible', 1, 'DATO DE DEMOSTRACIÓN');
