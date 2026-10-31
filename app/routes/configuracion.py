"""Configuración editable: porcentaje provisional, base del margen, vigencia, límites y textos."""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..db import get_db
from ..repositories import configuracion as repo
from ..validators import entradas as val

bp = Blueprint("configuracion", __name__, url_prefix="/configuracion")


@bp.route("/", methods=["GET", "POST"])
def editar():
    db = get_db()
    datos, errores = repo.obtener(db), {}
    if request.method == "POST":
        datos, errores = val.validar_configuracion(request.form)
        if not errores:
            repo.guardar(db, datos)
            flash("Configuración guardada.", "ok")
            return redirect(url_for("configuracion.editar"))
    return render_template("configuracion.html", datos=datos, errores=errores)
