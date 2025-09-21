from __future__ import annotations

from datetime import datetime
from io import StringIO

from flask import Blueprint, render_template, request, redirect, url_for, session, send_file, abort
from sqlalchemy import and_

from .models import db, User, Comentario


dashboard_bp = Blueprint("dashboard", __name__, template_folder="templates", static_folder="static")


def login_required(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("dashboard.login"))
        return func(*args, **kwargs)

    return wrapper


@dashboard_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            return redirect(url_for("dashboard.index"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@dashboard_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("dashboard.login"))


@dashboard_bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    categoria = request.args.get("categoria", "").strip()
    start = request.args.get("start")
    end = request.args.get("end")

    query = Comentario.query

    if q:
        query = query.filter(Comentario.texto.ilike(f"%{q}%"))
    if categoria:
        query = query.filter(Comentario.categoria == categoria)
    if start:
        try:
            dt_start = datetime.fromisoformat(start)
            query = query.filter(Comentario.created_at >= dt_start)
        except ValueError:
            pass
    if end:
        try:
            dt_end = datetime.fromisoformat(end)
            query = query.filter(Comentario.created_at <= dt_end)
        except ValueError:
            pass

    comentarios = query.order_by(Comentario.created_at.desc()).limit(500).all()

    categorias = ["ELOGIO", "CRÍTICA", "SUGESTÃO", "DÚVIDA", "SPAM"]
    return render_template("dashboard.html", comentarios=comentarios, categorias=categorias, params={
        "q": q,
        "categoria": categoria,
        "start": start or "",
        "end": end or "",
    })


@dashboard_bp.route("/export")
@login_required
def export_csv():
    q = request.args.get("q", "").strip()
    categoria = request.args.get("categoria", "").strip()
    start = request.args.get("start")
    end = request.args.get("end")

    query = Comentario.query
    if q:
        query = query.filter(Comentario.texto.ilike(f"%{q}%"))
    if categoria:
        query = query.filter(Comentario.categoria == categoria)
    if start:
        try:
            dt_start = datetime.fromisoformat(start)
            query = query.filter(Comentario.created_at >= dt_start)
        except ValueError:
            pass
    if end:
        try:
            dt_end = datetime.fromisoformat(end)
            query = query.filter(Comentario.created_at <= dt_end)
        except ValueError:
            pass

    rows = query.order_by(Comentario.created_at.desc()).all()

    import csv

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["id", "created_at", "categoria", "confianca", "tags_funcionalidades", "texto"])
    for r in rows:
        writer.writerow([
            r.id,
            r.created_at.isoformat() if r.created_at else "",
            r.categoria or "",
            r.confianca if r.confianca is not None else "",
            (", ".join(t.get("code", "") for t in (r.tags_funcionalidades or []))) if isinstance(r.tags_funcionalidades, list) else "",
            r.texto.replace("\n", " ") if r.texto else "",
        ])

    si.seek(0)
    return send_file(
        si,
        mimetype="text/csv",
        as_attachment=True,
        download_name="comentarios.csv",
    )

