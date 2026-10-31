"""Pruebas de integración: recorrido completo con el cliente de pruebas de Flask."""
import pytest

from app import create_app
from app.db import get_db
from app.engine.precios import formato_q


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "prueba.db"), "SECRET_KEY": "x"})


@pytest.fixture
def client(app):
    return app.test_client()


def datos_cotizacion(**cambios):
    d = {"cliente_id": "1", "vigencia_dias": "15", "mano_obra": "100", "transporte": "25.50", "otros": "10",
         "otros_detalle": "Empaques", "porcentaje": "30", "base": "recargo_sobre_costo", "observaciones": "Obs",
         "condiciones": "Condiciones de prueba", "accion": "guardar",
         "item_ident": ["Habitación 1: Ventana 1", "Habitación 2: Puerta 1"], "item_producto": ["1", "3"],
         "item_ancho": ["1,20", "0.90"], "item_alto": ["1.00", "2.10"], "item_cantidad": ["1", "2"],
         "item_hojas": ["2", "1"], "item_origen": ["tomada", "cliente"], "item_perfil": ["", "6"] if False else ["", ""],
         "item_vidrio": ["", ""], "item_notas": ["", ""]}
    d.update(cambios)
    return d


def guardar_cotizacion(client, **cambios):
    r = client.post("/cotizaciones/nueva", data=datos_cotizacion(**cambios))
    assert r.status_code == 302, r.get_data(as_text=True)[:2000]
    return r.headers["Location"]


def test_todas_las_pantallas_cargan(client):
    for url in ["/", "/clientes/", "/clientes/1", "/materiales/", "/productos/", "/productos/1",
                "/cotizaciones/", "/cotizaciones/nueva", "/inventario/", "/configuracion/"]:
        assert client.get(url).status_code == 200, url
    assert client.get("/no-existe").status_code == 404
    assert client.get("/clientes/999").status_code == 404


def test_cliente_crear_buscar_editar(client):
    r = client.post("/clientes/nuevo", data={"nombre": "Cliente Prueba", "telefono": "5555-1234"}, follow_redirects=True)
    assert "Cliente Prueba" in r.get_data(as_text=True)
    assert "Cliente Prueba" in client.get("/clientes/?q=5555-1234").get_data(as_text=True)
    r = client.post("/clientes/nuevo", data={"nombre": "", "telefono": "1"})
    assert "El nombre es obligatorio" in r.get_data(as_text=True)


def test_vista_previa_no_guarda(client, app):
    r = client.post("/cotizaciones/nueva", data=datos_cotizacion(accion="calcular"))
    html = r.get_data(as_text=True)
    assert r.status_code == 200 and "Vista previa del cálculo" in html and "VISTA INTERNA" in html
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM cotizaciones").fetchone()[0] == 0


def test_guardar_y_snapshot_de_precios(client, app):
    ubicacion = guardar_cotizacion(client)
    with app.app_context():
        db = get_db()
        antes = tuple(db.execute("SELECT precio_total_c, costo_total_c FROM cotizaciones WHERE id=1").fetchone())
        suma_antes = db.execute("SELECT SUM(subtotal_c) FROM cotizacion_detalle").fetchone()[0]
        assert db.execute("SELECT COUNT(*) FROM cotizacion_items").fetchone()[0] == 2
    # Subimos el precio del vidrio (material 2): la cotización guardada NO debe cambiar.
    r = client.post("/materiales/2/editar", data={"nombre": "Vidrio claro 6 mm (DEMO)", "categoria": "vidrio",
                    "unidad": "m2", "precio": "999.00", "activo": "1", "es_demo": "1"})
    assert r.status_code == 302
    with app.app_context():
        db = get_db()
        assert tuple(db.execute("SELECT precio_total_c, costo_total_c FROM cotizaciones WHERE id=1").fetchone()) == antes
        assert db.execute("SELECT SUM(subtotal_c) FROM cotizacion_detalle").fetchone()[0] == suma_antes
    assert "COT-0001" in client.get(ubicacion).get_data(as_text=True)


def test_version_cliente_no_muestra_datos_internos(client, app):
    guardar_cotizacion(client)
    with app.app_context():
        costo = get_db().execute("SELECT costo_total_c FROM cotizaciones WHERE id=1").fetchone()[0]
    html = client.get("/cotizaciones/1/imprimir").get_data(as_text=True)
    assert "COT-0001" in html and "TOTAL" in html
    for prohibido in ("Proveedor Demo", "Utilidad", "Costo total", "Mano de obra", "recargo", "Margen", formato_q(costo)):
        assert prohibido not in html, prohibido
    interno = client.get("/cotizaciones/1").get_data(as_text=True)
    assert "VISTA INTERNA" in interno and "Utilidad estimada" in interno


def test_estados_y_transiciones(client):
    guardar_cotizacion(client)
    client.post("/cotizaciones/1/estado", data={"estado": "aprobada"})
    r = client.post("/cotizaciones/1/estado", data={"estado": "pendiente"}, follow_redirects=True)
    html = r.get_data(as_text=True)
    assert "No se puede pasar de" in html and "Aprobada" in html
    assert "Estado final" not in html  # aprobada todavía puede cancelarse (supuesto documentado)


def test_duplicar_exacto_y_recalcular(client, app):
    guardar_cotizacion(client)
    client.post("/materiales/2/editar", data={"nombre": "Vidrio claro 6 mm (DEMO)", "categoria": "vidrio",
                "unidad": "m2", "precio": "500", "activo": "1", "es_demo": "1"})
    assert client.post("/cotizaciones/1/duplicar", data={"modo": "exacto"}).status_code == 302
    assert client.post("/cotizaciones/1/duplicar", data={"modo": "recalcular"}).status_code == 302
    with app.app_context():
        filas = get_db().execute("SELECT numero, precio_total_c, estado FROM cotizaciones ORDER BY numero").fetchall()
    assert [f["numero"] for f in filas] == [1, 2, 3]
    assert filas[1]["precio_total_c"] == filas[0]["precio_total_c"]      # mismos importes
    assert filas[2]["precio_total_c"] > filas[0]["precio_total_c"]       # precios vigentes (vidrio más caro)
    assert all(f["estado"] == "pendiente" for f in filas[1:])


@pytest.mark.parametrize("ancho", ["0", "-2", "abc", "", "NaN", "50"])
def test_medidas_invalidas_se_rechazan_en_el_servidor(client, app, ancho):
    r = client.post("/cotizaciones/nueva", data=datos_cotizacion(item_ancho=[ancho, "0.90"]))
    assert r.status_code == 200 and "Revisa lo siguiente" in r.get_data(as_text=True)
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM cotizaciones").fetchone()[0] == 0


def test_cliente_inexistente_y_perfil_incompatible(client):
    r = client.post("/cotizaciones/nueva", data=datos_cotizacion(cliente_id="999"))
    assert "Selecciona un cliente registrado" in r.get_data(as_text=True)
    # Perfil de aluminio (7) en la ventana de PVC (producto 1) no es válido.
    r = client.post("/cotizaciones/nueva", data=datos_cotizacion(item_perfil=["7", ""]))
    assert "no sirve para" in r.get_data(as_text=True)


def test_inventario_y_configuracion(client):
    r = client.post("/inventario/nuevo", data={"tipo": "sobrante", "forma": "lineal", "descripcion": "Perfil prueba",
                    "cantidad": "1", "largo_m": "1.5", "reutilizable": "1"}, follow_redirects=True)
    assert "Perfil prueba" in r.get_data(as_text=True)
    r = client.post("/inventario/nuevo", data={"tipo": "x", "forma": "y", "descripcion": ""}, follow_redirects=True)
    assert "La descripción es obligatoria" in r.get_data(as_text=True)
    r = client.post("/configuracion/", data={"nombre_negocio": "Negocio", "ubicacion_negocio": "X", "base_margen": "margen_sobre_precio",
                    "porcentaje": "100", "vigencia_dias": "10", "medida_min": "0.1", "medida_max": "10", "condiciones": "c"})
    assert "menor a 100" in r.get_data(as_text=True)


def test_acceso_desde_otra_red_bloqueado(app):
    r = app.test_client().get("/", environ_overrides={"REMOTE_ADDR": "203.0.113.9"})
    assert r.status_code == 403


def test_editar_receta_de_producto_cambia_el_calculo(client, app):
    with app.app_context():
        comps = get_db().execute("SELECT * FROM producto_componentes WHERE producto_id=5").fetchall()
    c = comps[0]
    datos = {"nombre": "Vidrio a medida", "descripcion": "x", "estado_datos": "demostracion", "activo": "1",
             "comp_id": [str(c["id"])], "comp_etiqueta": ["Vidrio"], "comp_regla": ["area"],
             "comp_factor": ["2"], "comp_desp": ["0"], "comp_material": [str(c["material_id"])]}
    assert client.post("/productos/5", data=datos).status_code == 302
    with app.app_context():
        assert get_db().execute("SELECT factor FROM producto_componentes WHERE id=?", (c["id"],)).fetchone()[0] == 2
    malos = dict(datos, comp_factor=["-1"])
    r = client.post("/productos/5", data=malos, follow_redirects=True)
    assert "Factor" in r.get_data(as_text=True)
