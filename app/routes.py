from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from concurrent.futures import ThreadPoolExecutor
from uuid import UUID

from .models import db, Comentario
from .services.llm import classificar_texto


api_bp = Blueprint("api", __name__)


@api_bp.route("/comentarios", methods=["POST"])
@jwt_required()
def add_comentarios():
    if not request.is_json:
        return jsonify(msg="Conteúdo deve ser JSON"), 400

    data = request.get_json(silent=True)
    if data is None:
        return jsonify(msg="JSON inválido"), 400

    if isinstance(data, dict):
        data = [data]
    elif not isinstance(data, list):
        return jsonify(msg="Payload deve ser objeto ou lista de objetos"), 400

    #faz a validação inicial e preparo
    textos = []
    ids = []
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            return jsonify(msg=f"Item {idx} inválido: deve ser um objeto"), 400
        texto = item.get("texto")
        if not isinstance(texto, str) or not texto.strip():
            return jsonify(msg=f"Item {idx} inválido: 'texto' obrigatório"), 400
        textos.append(texto.strip())

        provided_id = item.get("id")
        if provided_id is not None:
            try:
                UUID(str(provided_id))
            except Exception:
                return jsonify(msg=f"Item {idx} inválido: 'id' deve ser UUID"), 400
            ids.append(str(provided_id))
        else:
            ids.append(None)

    #classificação em paralelo (sem tocar no DB dentro das threads)
    max_workers = min(8, len(textos)) or 1
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        resultados = list(executor.map(classificar_texto, textos))

    resposta = []
    #persistência sequencial com uma única transação
    for i, texto in enumerate(textos):
        resultado = resultados[i]
        comentario = Comentario(
            texto=texto,
            categoria=resultado.get("categoria"),
            tags_funcionalidades=resultado.get("tags_funcionalidades"),
            confianca=resultado.get("confianca"),
        )
        if ids[i] is not None:
            comentario.id = ids[i]
        db.session.add(comentario)
        resposta.append({
            "id": comentario.id,
            "texto": comentario.texto,
            "categoria": comentario.categoria,
            "tags_funcionalidades": comentario.tags_funcionalidades,
            "confianca": comentario.confianca,
        })

    db.session.commit()
    return jsonify(resposta), 201

