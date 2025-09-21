from __future__ import annotations

from typing import Dict, List, Tuple

#as categorias oficiais do desafio
CATEGORIAS = {"ELOGIO", "CRÍTICA", "SUGESTÃO", "DÚVIDA", "SPAM"}


def _normalize(text: str) -> str:
    return text.lower()


def _detect_category(text: str) -> Tuple[str, float]:
    t = _normalize(text)

    spam_kw = ["http://", "https://", "promo", "ganhe", "siga", "desconto", "cupom"]
    if any(k in t for k in spam_kw):
        return "SPAM", 0.95

    if "?" in t or any(k in t for k in ["como", "quando", "onde", "por que", "pq"]):
        return "DÚVIDA", 0.9

    if "sugest" in t or any(k in t for k in ["poderia", "seria legal", "deveria"]):
        return "SUGESTÃO", 0.85

    elogio_kw = ["amei", "incrível", "maravilha", "bom", "ótimo", "excelente", "curti", "perfeito"]
    if any(k in t for k in elogio_kw):
        return "ELOGIO", 0.85

    critica_kw = ["ruim", "horrível", "péssimo", "não gostei", "odiei", "critica", "crítica", "fraco"]
    if any(k in t for k in critica_kw):
        return "CRÍTICA", 0.8

    #fallback pouco confiante
    return "CRÍTICA", 0.6


def _extract_tags(text: str) -> List[Dict[str, str]]:
    t = _normalize(text)
    tags: List[Dict[str, str]] = []

    if "autotune" in t:
        tags.append({
            "code": "feat_autotune",
            "explanation": "O comentário menciona uso de autotune."
        })
    if any(k in t for k in ["clipe", "vídeo", "video", "narrativa"]):
        tags.append({
            "code": "clip_narrativa",
            "explanation": "Menciona o clipe/vídeo ou sua narrativa."
        })
    if any(k in t for k in ["show", "turnê", "turne", "duração", "duracao", "luz", "som"]):
        tags.append({
            "code": "show_producao",
            "explanation": "Cita aspectos do show (duração, luz, som)."
        })
    if any(k in t for k in ["álbum", "album", "faixa", "música", "musica", "single"]):
        tags.append({
            "code": "album_faixa",
            "explanation": "Refere-se ao álbum, faixa ou música."
        })

    #limitar a 3 para resposta concisa
    return tags[:3]


def classificar_texto(texto: str) -> dict:
    """
    Classificador heurístico simples (determinístico) para desenvolvimento e testes.
    Estrutura compatível com o contrato do desafio.
    """
    categoria, base_conf = _detect_category(texto)
    tags = _extract_tags(texto)

    #ajuste leve de confiança baseado na quantidade de evidências
    boost = 0.02 * len(tags)
    confianca = min(round(base_conf + boost, 2), 0.99)

    #garantir que a categoria está no conjunto previsto
    if categoria not in CATEGORIAS:
        categoria = "CRÍTICA"

    return {
        "categoria": categoria,
        "tags_funcionalidades": tags,
        "confianca": confianca,
    }

