from __future__ import annotations

import base64
import io
from datetime import datetime, timedelta
from typing import Dict, Any

import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from flask import Blueprint, jsonify, request, render_template_string
from flask_caching import Cache

from .models import db, Comentario


reports_bp = Blueprint("reports", __name__)


def _df_comentarios() -> pd.DataFrame:
    rows = Comentario.query.all()
    data = [
        {
            "created_at": r.created_at,
            "categoria": r.categoria or "",
            "confianca": r.confianca or 0.0,
            "tags": [t.get("code") for t in (r.tags_funcionalidades or [])],
            "texto": r.texto,
        }
        for r in rows
    ]
    if not data:
        return pd.DataFrame(columns=["created_at", "categoria", "confianca", "tags", "texto"])  # empty
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["created_at"]).dt.date
    return df


def _png_from_fig(fig) -> str:
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")


def _charts(df: pd.DataFrame) -> Dict[str, str]:
    charts: Dict[str, str] = {}
    if df.empty:
        # create a placeholder empty chart
        fig, ax = plt.subplots(figsize=(4, 2))
        ax.text(0.5, 0.5, "Sem dados", ha="center", va="center")
        ax.axis("off")
        charts["placeholder"] = _png_from_fig(fig)
        return charts

    # 1) Volume por dia
    fig, ax = plt.subplots(figsize=(6, 3))
    df.groupby("date").size().plot(kind="bar", ax=ax, color="#4e79a7")
    ax.set_title("Volume de comentários por dia")
    ax.set_xlabel("Data")
    ax.set_ylabel("Qtde")
    charts["volume_dia"] = _png_from_fig(fig)

    # 2) Categorias mais frequentes (geral)
    fig, ax = plt.subplots(figsize=(6, 3))
    df["categoria"].value_counts().plot(kind="bar", ax=ax, color="#f28e2b")
    ax.set_title("Categorias mais frequentes (geral)")
    ax.set_xlabel("Categoria")
    ax.set_ylabel("Qtde")
    charts["categorias"] = _png_from_fig(fig)

    # 3) Evolução de críticas por dia
    fig, ax = plt.subplots(figsize=(6, 3))
    (
        df[df["categoria"] == "CRÍTICA"].groupby("date").size()
    ).plot(kind="line", marker="o", ax=ax, color="#e15759")
    ax.set_title("Evolução de CRÍTICA por dia")
    ax.set_xlabel("Data")
    ax.set_ylabel("Qtde")
    charts["critica_evolucao"] = _png_from_fig(fig)

    # 4) Top tags últimas 48h
    cutoff = datetime.utcnow().date() - timedelta(days=2)
    recent = df[df["date"] >= cutoff]
    tags = []
    for lst in recent["tags"].dropna().tolist():
        tags.extend(lst or [])
    tag_counts = pd.Series(tags).value_counts().head(10)
    fig, ax = plt.subplots(figsize=(6, 3))
    if not tag_counts.empty:
        tag_counts.plot(kind="bar", ax=ax, color="#76b7b2")
        ax.set_ylabel("Qtde")
    ax.set_title("Top tags últimas 48h")
    ax.set_xlabel("Tag")
    charts["tags_48h"] = _png_from_fig(fig)

    # 5) Distribuição de confiança por categoria (média)
    conf = df.groupby("categoria")["confianca"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(6, 3))
    conf.plot(kind="bar", ax=ax, color="#59a14f")
    ax.set_title("Confiança média por categoria")
    ax.set_xlabel("Categoria")
    ax.set_ylabel("Confiança média")
    charts["confianca_categoria"] = _png_from_fig(fig)

    return charts


@reports_bp.route("/relatorio/semana")
def weekly_report():
    # cache por 60s (configurado no app)
    df = _df_comentarios()
    charts = _charts(df)

    # JSON se solicitado
    if request.args.get("format") == "json" or request.headers.get("Accept", "").startswith("application/json"):
        # Dados agregados para quem quiser consumir
        payload: Dict[str, Any] = {
            "updated_at": datetime.utcnow().isoformat(),
            "charts": {k: f"data:image/png;base64,{v}" for k, v in charts.items()},
        }
        return jsonify(payload)

    # HTML simples com imagens embutidas
    html = """
    <!doctype html>
    <html lang="pt-BR">
    <head><meta charset="utf-8"><title>Relatório Semanal</title></head>
    <body style="font-family:system-ui, Arial, sans-serif; padding:16px;">
      <h1>Relatório Semanal</h1>
      {% for title, key in [
        ("Volume por dia", "volume_dia"),
        ("Categorias mais frequentes", "categorias"),
        ("Evolução de críticas", "critica_evolucao"),
        ("Top tags 48h", "tags_48h"),
        ("Confiança por categoria", "confianca_categoria"),
      ] %}
        <section style="margin-bottom:24px;">
          <h3>{{ title }}</h3>
          {% if charts.get(key) %}
            <img alt="{{ title }}" style="max-width:100%;" src="data:image/png;base64,{{ charts[key] }}" />
          {% else %}
            <p>Sem dados.</p>
          {% endif %}
        </section>
      {% endfor %}
    </body></nhtml>
    """
    return render_template_string(html, charts=charts)

