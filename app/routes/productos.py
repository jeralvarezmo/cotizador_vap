"""Rutas de productos y de sus recetas editables."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..db import get_db
from ..repositories import materiales as repo_mat
from ..repositories import productos as repo
from ..validators import entradas as val

bp = Blueprint("productos", __name__, url_prefix="/productos")


@bp.route("/")
def lista():
    return render_template("productos/lista.html", productos=repo.listar(get_db()))


@bp.route("/<int:pid>")
def detalle(pid):
    db = get_db()
    p = repo.obtener(db, pid)
    if p is None:
        abort(404)
    return render_template("productos/detalle.html", p=p, comps=repo.componentes(db, pid),
                           materiales=repo_mat.listar(db, estado="activos"))


@bp.post("/<int:pid>")
def guardar(pid):
    db = get_db()
    if repo.obtener(db, pid) is None:
        abort(404)
    datos, errores = val.validar_producto(request.form)
    comps, errores_comp = val.validar_componentes(request.form)
    todos = list(errores.values()) + errores_comp
    if todos:
        for e in todos:
            flash(e, "error")
    else:
        repo.actualizar(db, pid, datos, comps)
        flash("Producto y receta actualizados.", "ok")
    return redirect(url_for("productos.detalle", pid=pid))
