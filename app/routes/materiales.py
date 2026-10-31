"""Rutas de materiales y precios vigentes."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..db import get_db
from ..repositories import materiales as repo
from ..validators import entradas as val

bp = Blueprint("materiales", __name__, url_prefix="/materiales")


@bp.route("/")
def lista():
    categoria, estado, q = request.args.get("categoria", ""), request.args.get("estado", ""), request.args.get("q", "").strip()
    filas = repo.listar(get_db(), categoria or None, estado or None, q or None)
    return render_template("materiales/lista.html", materiales=filas, categoria=categoria, estado=estado, q=q)


@bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    datos, errores = {"activo": 1, "es_demo": 0}, {}
    if request.method == "POST":
        datos, errores = val.validar_material(request.form)
        if not errores:
            repo.crear(get_db(), datos)
            flash("Material registrado.", "ok")
            return redirect(url_for("materiales.lista"))
    return render_template("materiales/form.html", titulo="Nuevo material", datos=datos, errores=errores)


@bp.route("/<int:mid>/editar", methods=["GET", "POST"])
def editar(mid):
    db = get_db()
    m = repo.obtener(db, mid)
    if m is None:
        abort(404)
    datos, errores = {**dict(m), "precio": f"{m['precio_centavos'] / 100:.2f}"}, {}
    if request.method == "POST":
        datos, errores = val.validar_material(request.form)
        if not errores:
            repo.actualizar(db, mid, datos)
            flash("Material actualizado. Las cotizaciones ya guardadas conservan sus importes originales.", "ok")
            return redirect(url_for("materiales.lista"))
    return render_template("materiales/form.html", titulo="Editar material", datos=datos, errores=errores)
