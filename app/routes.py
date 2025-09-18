from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from .models import db, Comentario

api_bp = Blueprint("api", __name__)


@api_bp.route("/comentarios", methods=["POST"])
@jwt_required()
def add_comentarios():
    if not request.is_json:
        return jsonify(msg="Conteúdo deve ser JSON"), 400

    data = request.get_json(silent=True)
    if data is None:
        return jsonify(msg="JSON inválido"), 400

    if isinstance(data, dict):  # um comentário
        data = [data]
    elif not isinstance(data, list):
        return jsonify(msg="Payload deve ser objeto ou lista de objetos"), 400

    comentarios = []
    for idx, item in enumerate(data):
        if not isinstance(item, dict) or not item.get("texto") or not isinstance(item.get("texto"), str):
            return jsonify(msg=f"Item {idx} inválido: 'texto' obrigatório"), 400
        comentario = Comentario(texto=item["texto"].strip())
        db.session.add(comentario)
        comentarios.append({"id": comentario.id, "texto": comentario.texto})

    db.session.commit()
    return jsonify(comentarios), 201

