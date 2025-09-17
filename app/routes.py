from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from .models import db, Comentario

api_bp = Blueprint("api", __name__)

@api_bp.route("/comentarios", methods=["POST"])
@jwt_required()
def add_comentarios():
    data = request.get_json()

    if isinstance(data, dict):  # um comentário
        data = [data]

    comentarios = []
    for item in data:
        comentario = Comentario(texto=item["texto"])
        db.session.add(comentario)
        comentarios.append({"id": comentario.id, "texto": comentario.texto})

    db.session.commit()
    return jsonify(comentarios), 201
