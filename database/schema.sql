-- ESQUEMA DE LA BASE DE DATOS (SQLite)
-- Convenciones: dinero en CENTAVOS (enteros), medidas en METROS (provisional),
-- fechas como texto ISO (AAAA-MM-DD). Las claves foráneas se activan en db.py.

PRAGMA foreign_keys = ON;

CREATE TABLE configuracion (
    clave       TEXT PRIMARY KEY,
    valor       TEXT NOT NULL,
    descripcion TEXT
);

CREATE TABLE clientes (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre        TEXT NOT NULL CHECK (length(trim(nombre)) > 0),
    telefono      TEXT,
    correo        TEXT,
    direccion     TEXT,
    observaciones TEXT,
    creado_en     TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE materiales (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre          TEXT NOT NULL,
    categoria       TEXT NOT NULL,
    unidad          TEXT NOT NULL,
    caracteristicas TEXT,
    proveedor       TEXT,
    precio_centavos INTEGER NOT NULL DEFAULT 0 CHECK (precio_centavos >= 0),
    activo          INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1)),
    es_demo         INTEGER NOT NULL DEFAULT 0 CHECK (es_demo IN (0, 1)),
    actualizado_en  TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE productos (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo       TEXT NOT NULL UNIQUE,
    nombre       TEXT NOT NULL,
    categoria    TEXT NOT NULL,
    descripcion  TEXT,
    estado_datos TEXT NOT NULL DEFAULT 'demostracion'
                 CHECK (estado_datos IN ('demostracion', 'supuesto', 'confirmado')),
    activo       INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1))
);

-- "Receta" de un producto: lista de componentes con una regla de cantidad.
-- Las reglas reales del negocio están PENDIENTES: estas recetas son editables.
CREATE TABLE producto_componentes (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id           INTEGER NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
    etiqueta              TEXT NOT NULL,
    rol                   TEXT NOT NULL DEFAULT 'otro',   -- 'perfil' y 'vidrio' se eligen al cotizar
    categorias_permitidas TEXT NOT NULL,                  -- categorías de material, separadas por coma
    material_id           INTEGER REFERENCES materiales(id),
    regla                 TEXT NOT NULL
                          CHECK (regla IN ('perimetro', 'area', 'ancho', 'alto', 'fijo', 'por_hoja')),
    factor                REAL NOT NULL DEFAULT 1 CHECK (factor >= 0),
    desperdicio_pct       REAL NOT NULL DEFAULT 0 CHECK (desperdicio_pct >= 0 AND desperdicio_pct <= 100),
    orden                 INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE cotizaciones (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    numero             INTEGER NOT NULL UNIQUE,            -- número visible (COT-0001)
    fecha              TEXT NOT NULL,
    cliente_id         INTEGER NOT NULL REFERENCES clientes(id),
    estado             TEXT NOT NULL DEFAULT 'pendiente'
                       CHECK (estado IN ('pendiente', 'aprobada', 'rechazada', 'cancelada')),
    vigencia_dias      INTEGER NOT NULL,
    vigencia_hasta     TEXT NOT NULL,
    observaciones      TEXT,
    condiciones        TEXT,
    costo_materiales_c INTEGER NOT NULL,
    mano_obra_c        INTEGER NOT NULL DEFAULT 0,
    transporte_c       INTEGER NOT NULL DEFAULT 0,
    otros_c            INTEGER NOT NULL DEFAULT 0,
    otros_detalle      TEXT,
    costo_total_c      INTEGER NOT NULL,
    base_margen        TEXT NOT NULL,                      -- recargo_sobre_costo | margen_sobre_precio
    porcentaje         REAL NOT NULL,
    utilidad_c         INTEGER NOT NULL,
    precio_total_c     INTEGER NOT NULL,
    usa_demo           INTEGER NOT NULL DEFAULT 1,         -- 1 si se usaron datos de demostración
    creado_en          TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    actualizado_en     TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);
CREATE INDEX idx_cotizaciones_cliente ON cotizaciones(cliente_id);
CREATE INDEX idx_cotizaciones_estado  ON cotizaciones(estado);

-- Cada elemento de una cotización (ej.: "Habitación 1: Ventana 1").
CREATE TABLE cotizacion_items (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    cotizacion_id         INTEGER NOT NULL REFERENCES cotizaciones(id) ON DELETE CASCADE,
    orden                 INTEGER NOT NULL,
    identificacion        TEXT,
    producto_id           INTEGER REFERENCES productos(id),
    producto_nombre       TEXT NOT NULL,                   -- copia histórica
    producto_estado_datos TEXT NOT NULL,
    ancho_m               REAL NOT NULL CHECK (ancho_m > 0),
    alto_m                REAL NOT NULL CHECK (alto_m > 0),
    origen_medida         TEXT NOT NULL,                   -- cliente | tomada | fabricacion
    cantidad              INTEGER NOT NULL CHECK (cantidad > 0),
    hojas                 INTEGER NOT NULL DEFAULT 1,
    perfil_id             INTEGER REFERENCES materiales(id),
    vidrio_id             INTEGER REFERENCES materiales(id),
    notas                 TEXT,
    area_m2               REAL NOT NULL,
    perimetro_m           REAL NOT NULL,
    costo_materiales_c    INTEGER NOT NULL,
    precio_c              INTEGER NOT NULL
);

-- SNAPSHOT: copia de lo que se usó al cotizar. No cambia si el material sube de precio.
CREATE TABLE cotizacion_detalle (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id         INTEGER NOT NULL REFERENCES cotizacion_items(id) ON DELETE CASCADE,
    concepto        TEXT NOT NULL,
    rol             TEXT,
    material_id     INTEGER REFERENCES materiales(id),
    material_nombre TEXT NOT NULL,
    unidad          TEXT NOT NULL,
    cantidad        REAL NOT NULL,
    precio_unit_c   INTEGER NOT NULL,
    subtotal_c      INTEGER NOT NULL,
    es_demo         INTEGER NOT NULL DEFAULT 0,
    regla_texto     TEXT
);

CREATE TABLE cotizacion_historial (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    cotizacion_id   INTEGER NOT NULL REFERENCES cotizaciones(id) ON DELETE CASCADE,
    fecha_hora      TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    accion          TEXT NOT NULL,
    estado_anterior TEXT,
    estado_nuevo    TEXT,
    nota            TEXT
);

-- Registro BÁSICO (manual) de existencias y sobrantes. No descuenta nada automáticamente.
CREATE TABLE inventario (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo           TEXT NOT NULL CHECK (tipo IN ('existencia', 'sobrante')),
    material_id    INTEGER REFERENCES materiales(id),
    descripcion    TEXT NOT NULL,
    forma          TEXT NOT NULL CHECK (forma IN ('lineal', 'plana', 'unidades')),
    cantidad       REAL NOT NULL DEFAULT 1 CHECK (cantidad >= 0),
    largo_m        REAL,                                   -- perfiles (forma lineal)
    ancho_m        REAL,                                   -- vidrio (forma plana)
    alto_m         REAL,
    espesor        TEXT,
    serie          TEXT,
    color          TEXT,
    ubicacion      TEXT,
    estado         TEXT NOT NULL DEFAULT 'disponible'
                   CHECK (estado IN ('disponible', 'reservado', 'reutilizado', 'baja')),
    reutilizable   INTEGER NOT NULL DEFAULT 1 CHECK (reutilizable IN (0, 1)),
    observaciones  TEXT,
    fecha_registro TEXT NOT NULL DEFAULT (date('now', 'localtime'))
);
