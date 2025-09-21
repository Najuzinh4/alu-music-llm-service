from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from .models import db, WeeklySummary
from .services.llm import responder_insight


insights_bp = Blueprint("insights", __name__)


@insights_bp.route("/perguntar", methods=["POST"])
@jwt_required()
def perguntar():
    payload = request.get_json(silent=True) or {}
    pergunta = (payload.get("pergunta") or "").strip()
    if not pergunta:
        return jsonify(error="Campo 'pergunta' é obrigatório"), 400

    # Seleciona os três resumos semanais mais recentes das últimas 8 semanas
    limite = datetime.utcnow() - timedelta(weeks=8)
    summaries: List[WeeklySummary] = (
        WeeklySummary.query.filter(WeeklySummary.created_at >= limite)
        .order_by(WeeklySummary.created_at.desc())
        .limit(3)
        .all()
    )

    if not summaries:
        return jsonify(error="Sem resumos disponíveis"), 400

    contexto = "\n\n".join(s.content for s in summaries)
    resposta = responder_insight(contexto, pergunta, max_palavras=150)

    return jsonify({
        "resposta": resposta,
        "semanas": [s.week for s in summaries],
    })

