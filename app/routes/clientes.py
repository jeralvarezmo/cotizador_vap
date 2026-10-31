"""Rutas de clientes: lista/búsqueda, ficha, alta y edición."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..db import get_db
from ..repositories import clientes as repo
from ..repositories import cotizaciones as repo_cot
from ..validators import entradas as val

bp = Blueprint("clientes", __name__, url_prefix="/clientes")


@bp.route("/")
def lista():
    q = request.args.get("q", "").strip()
    return render_template("clientes/lista.html", clientes=repo.listar(get_db(), q), q=q)


@bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    datos, errores = {}, {}
    if request.method == "POST":
        datos, errores = val.validar_cliente(request.form)
        if not errores:
            cid = repo.crear(get_db(), datos)
            flash("Cliente registrado.", "ok")
            return redirect(url_for("clientes.detalle", cid=cid))
    return render_template("clientes/form.html", titulo="Nuevo cliente", datos=datos, errores=errores)


@bp.route("/<int:cid>")
def detalle(cid):
    db = get_db()
    cliente = repo.obtener(db, cid)
    if cliente is None:
        abort(404)
    return render_template("clientes/detalle.html", c=cliente, cotizaciones=repo_cot.listar(db, cliente_id=cid))


@bp.route("/<int:cid>/editar", methods=["GET", "POST"])
def editar(cid):
    db = get_db()
    cliente = repo.obtener(db, cid)
    if cliente is None:
        abort(404)
    datos, errores = dict(cliente), {}
    if request.method == "POST":
        datos, errores = val.validar_cliente(request.form)
        if not errores:
            repo.actualizar(db, cid, datos)
            flash("Datos del cliente actualizados.", "ok")
            return redirect(url_for("clientes.detalle", cid=cid))
    return render_template("clientes/form.html", titulo="Editar cliente", datos=datos, errores=errores)
