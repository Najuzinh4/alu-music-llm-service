from __future__ import annotations

from datetime import datetime
from io import StringIO

import os
from flask import Blueprint, render_template, request, redirect, url_for, session, send_file, abort, jsonify, send_from_directory
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
            # Após login, vai para a SPA React por padrão
            return redirect(url_for("dashboard.app_ui"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@dashboard_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("dashboard.login"))


@dashboard_bp.route("/")
@login_required
def index():
    # Se existir build do React, redireciona para a SPA por padrão
    ui_index = os.path.join(dashboard_bp.root_path, "static", "ui", "index.html")
    if os.path.isfile(ui_index):
        return redirect(url_for("dashboard.app_ui"))
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


#fiz a apo de dados para o frontend React (protegida por sessão)
@dashboard_bp.route("/data/comentarios")
@login_required
def data_comentarios():
    q = request.args.get("q", "").strip()
    categoria = request.args.get("categoria", "").strip()
    start = request.args.get("start")
    end = request.args.get("end")
    page = max(int(request.args.get("page", 1) or 1), 1)
    per_page = min(max(int(request.args.get("per_page", 50) or 50), 1), 200)

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

    total = query.count()
    items = (
        query.order_by(Comentario.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    def serialize(r: Comentario):
        return {
            "id": r.id,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "categoria": r.categoria,
            "confianca": r.confianca,
            "tags_funcionalidades": r.tags_funcionalidades or [],
            "texto": r.texto,
        }

    return jsonify({
        "total": total,
        "page": page,
        "per_page": per_page,
        "items": [serialize(r) for r in items],
    })


#pra servi build do React (se existir)
@dashboard_bp.route("/app")
@login_required
def app_ui():
    base = os.path.join(dashboard_bp.root_path, "static", "ui")
    index_path = os.path.join(base, "index.html")
    if os.path.isfile(index_path):
        return send_from_directory(base, "index.html")
    #sem o build da da SPA, cai para o dashboard clássico
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/app/<path:path>")
@login_required
def app_ui_assets(path: str):
    #serve os assets do build do Vite e se não existir, devolve index.html (spa fallback)
    base = os.path.join(dashboard_bp.root_path, "static", "ui")
    file_path = os.path.join(base, path)
    if os.path.isfile(file_path):
        rel = os.path.relpath(file_path, base)
        return send_from_directory(base, rel)
    index_path = os.path.join(base, "index.html")
    if os.path.isfile(index_path):
        return send_from_directory(base, "index.html")
    return redirect(url_for("dashboard.index"))
