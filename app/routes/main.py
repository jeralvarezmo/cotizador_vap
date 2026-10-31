"""Pantalla de inicio (dashboard)."""
from flask import Blueprint, render_template

from ..db import get_db
from ..repositories import clientes as repo_cli
from ..repositories import cotizaciones as repo_cot

bp = Blueprint("main", __name__)


@bp.route("/")
def inicio():
    db = get_db()
    conteos = repo_cot.contar_por_estado(db)
    return render_template("dashboard.html", n_clientes=repo_cli.contar(db), conteos=conteos,
                           total=sum(conteos.values()), recientes=repo_cot.listar(db, limite=6))
