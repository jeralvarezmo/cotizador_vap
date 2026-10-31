"""Fábrica de la aplicación Flask (create_app)."""
import os
import secrets

from flask import Flask, abort, render_template, request

from . import db
from .filtros import registrar_filtros


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # Sin secretos en el código: la clave se toma del entorno o se genera al arrancar.
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        DATABASE=os.path.join(app.instance_path, "cotizador.db"),
        PERMITIR_RED=os.environ.get("COTIZADOR_PERMITIR_RED") == "1",
    )
    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)
    registrar_filtros(app)

    from .routes import clientes, configuracion, cotizaciones, inventario, main, materiales, productos

    for modulo in (main, clientes, materiales, productos, cotizaciones, inventario, configuracion):
        app.register_blueprint(modulo.bp)

    @app.before_request
    def solo_local():
        # Mientras no exista autenticación, solo se acepta tráfico de esta computadora.
        if not app.config["PERMITIR_RED"] and request.remote_addr not in ("127.0.0.1", "::1"):
            abort(403)

    def _error(codigo, titulo, mensaje):
        return render_template("error.html", codigo=codigo, titulo=titulo, mensaje=mensaje), codigo

    @app.errorhandler(403)
    def e403(_e):
        return _error(403, "Acceso restringido", "Esta aplicación aún no tiene inicio de sesión, por eso solo acepta conexiones desde esta misma computadora.")

    @app.errorhandler(404)
    def e404(_e):
        return _error(404, "No encontrado", "La página o el registro que buscas no existe.")

    @app.errorhandler(500)
    def e500(_e):
        return _error(500, "Error interno", "Ocurrió un error inesperado. Revisa la terminal para ver el detalle.")

    if not os.path.exists(app.config["DATABASE"]):
        with app.app_context():
            db.init_db()  # primera ejecución: crea la BD con datos de demostración
    return app
