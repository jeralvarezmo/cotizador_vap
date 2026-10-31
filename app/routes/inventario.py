"""Registro básico de existencias y sobrantes (manual; no descuenta materiales)."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..catalogos import ESTADOS_INVENTARIO
from ..db import get_db
from ..repositories import inventario as repo
from ..repositories import materiales as repo_mat
from ..validators import entradas as val

bp = Blueprint("inventario", __name__, url_prefix="/inventario")


@bp.route("/")
def lista():
    tipo, estado = request.args.get("tipo", ""), request.args.get("estado", "")
    db = get_db()
    return render_template("inventario.html", filas=repo.listar(db, tipo or None, estado or None),
                           materiales=repo_mat.listar(db), tipo=tipo, estado=estado)


@bp.post("/nuevo")
def nuevo():
    datos, errores = val.validar_inventario(request.form)
    if errores:
        for e in errores.values():
            flash(e, "error")
    else:
        repo.crear(get_db(), datos)
        flash("Registro de inventario agregado.", "ok")
    return redirect(url_for("inventario.lista"))


@bp.post("/<int:iid>/estado")
def estado(iid):
    nuevo_estado = request.form.get("estado")
    if nuevo_estado not in ESTADOS_INVENTARIO:
        abort(400)
    repo.cambiar_estado(get_db(), iid, nuevo_estado)
    flash("Estado actualizado.", "ok")
    return redirect(url_for("inventario.lista"))
