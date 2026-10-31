"""Rutas de cotizaciones: lista, nueva (calcular/guardar), detalle, estado, duplicar e impresión."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..db import get_db
from ..engine.estados import TRANSICIONES
from ..engine.precios import porcentaje_sobre
from ..repositories import clientes as repo_cli
from ..repositories import configuracion as repo_cfg
from ..repositories import cotizaciones as repo
from ..repositories import materiales as repo_mat
from ..repositories import productos as repo_prod
from ..services import cotizaciones as servicio

bp = Blueprint("cotizaciones", __name__, url_prefix="/cotizaciones")


def _catalogos(db):
    cats = repo_prod.categorias_perfil(db)
    productos = [{**dict(p), "cats_perfil": cats.get(p["id"], "")} for p in repo_prod.listar(db, solo_activos=True)]
    activos = repo_mat.listar(db, estado="activos")
    return {"clientes": repo_cli.listar(db), "productos": productos,
            "perfiles": [m for m in activos if m["categoria"] in ("perfil_aluminio", "perfil_pvc")],
            "vidrios": [m for m in activos if m["categoria"] == "vidrio"]}


@bp.route("/")
def lista():
    estado, q = request.args.get("estado", ""), request.args.get("q", "").strip()
    return render_template("cotizaciones/lista.html", cotizaciones=repo.listar(get_db(), estado or None, q or None),
                           estado=estado, q=q)


@bp.route("/nueva", methods=["GET", "POST"])
def nueva():
    db = get_db()
    res = None
    if request.method == "POST":
        filas = servicio.leer_filas(request.form)
        res = servicio.preparar(db, request.form, filas)
        if request.form.get("accion") == "guardar" and not res["errores"]:
            cid = servicio.guardar(db, res)
            flash("Cotización guardada con el detalle y los precios utilizados.", "ok")
            return redirect(url_for("cotizaciones.detalle", cid=cid))
        valores = request.form
    else:
        valores = servicio.valores_iniciales(repo_cfg.obtener(db))
        valores["cliente_id"] = request.args.get("cliente_id", "")
        filas = []
    return render_template("cotizaciones/nueva.html", valores=valores, filas=filas or [servicio.fila_vacia()],
                           fila_vacia=servicio.fila_vacia(), res=res, **_catalogos(db))


@bp.route("/<int:cid>")
def detalle(cid):
    db = get_db()
    c = repo.obtener(db, cid)
    if c is None:
        abort(404)
    resumen = dict(c)
    resumen["utilidad_sobre_costo"] = porcentaje_sobre(c["utilidad_c"], c["costo_total_c"])
    resumen["utilidad_sobre_precio"] = porcentaje_sobre(c["utilidad_c"], c["precio_total_c"])
    return render_template("cotizaciones/detalle.html", c=c, items=repo.items(db, cid), resumen=resumen,
                           historial=repo.historial(db, cid), siguientes=TRANSICIONES[c["estado"]])


@bp.post("/<int:cid>/estado")
def estado(cid):
    try:
        servicio.cambiar_estado(get_db(), cid, request.form.get("estado", ""), request.form.get("nota", "").strip()[:200])
        flash("Estado actualizado.", "ok")
    except LookupError:
        abort(404)
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("cotizaciones.detalle", cid=cid))


@bp.post("/<int:cid>/duplicar")
def duplicar(cid):
    recalcular = request.form.get("modo") == "recalcular"
    try:
        nuevo = servicio.duplicar(get_db(), cid, recalcular)
    except LookupError:
        abort(404)
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for("cotizaciones.detalle", cid=cid))
    flash("Cotización duplicada como nueva (pendiente).", "ok")
    return redirect(url_for("cotizaciones.detalle", cid=nuevo))


@bp.route("/<int:cid>/imprimir")
def imprimir(cid):
    """Versión para el cliente: sin costos, proveedores, margen ni utilidad."""
    db = get_db()
    c = repo.obtener(db, cid)
    if c is None:
        abort(404)
    return render_template("cotizaciones/imprimir.html", c=c, items=repo.items(db, cid), cfg=repo_cfg.obtener(db))
