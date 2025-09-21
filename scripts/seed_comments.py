from __future__ import annotations

from app.main import create_app
from app.models import db, Comentario
from app.services.llm import classificar_texto


SAMPLE_COMMENTS = [
    "Amei o álbum novo, produção incrível!",
    "O clipe ficou ruim, não gostei da narrativa.",
    "Poderia aumentar a duração do show?",
    "Quando sai o próximo single?",
    "Ganhe descontos clicando aqui: http://spam.me",
    "Show perfeito, som e luz impecáveis!",
    "A faixa 3 está fraca, letra ruim.",
    "Seria legal lançar um acústico ao vivo.",
    "Onde encontro a versão sem autotune?",
    "Promo exclusiva: siga meu perfil para cupom!",
    "O álbum é bom, mas esperava mais.",
    "Adorei a performance ao vivo, arrasaram!",
    "Não entendi a mensagem da música.",
    "Visite nosso site para ofertas imperdíveis!",
    "A voz está muito autotuneada, não curti.",
    "Show de luzes e efeitos sensacional!",
    "O clipe é top, adorei a produção visual.", 
    "Lixo de álbum, uma decepção total.",
    "Amei a vibe do álbum, hit atrás de hit!",
    "Achei o clipe meio confuso, não gostei.",
    "Compre já o álbum e ganhe brindes!",
    "A voz da cantora é maravilhosa, perfeita!",
    "O som do show estava péssimo, não dava pra ouvir.",
    "Seria bom ter mais interações com o público.",
    "Qual é a inspiração por trás da letra?",
    "Clique aqui para baixar o álbum grátis!",
    "A produção do álbum está impecável, adorei!",
    "O clipe não faz sentido, fiquei perdido.",
    "Gostaria que lançassem mais versões acústicas.",
    "Por que não há mais músicas como essa?",
    "Visite nosso site para mais novidades!",
    "A faixa 5 é um hino, não paro de ouvir!",
    "O álbum é uma bosta, não recomendo.",
    "Show inesquecível, melhor que o anterior!",
    "A letra da música é profunda, adorei.",
    "Promoção relâmpago: compre 1, leve 2!",
    "A voz ao vivo é ainda melhor que no álbum.",
    "O som estava distorcido, arruinaram o show.",
    "Poderia ter mais baladas no próximo álbum.",
    "Onde posso encontrar a letra completa?",
    "Siga nosso perfil para mais promoções!",
    "Amei cada faixa do álbum, perfeito!",
    "O clipe é uma obra de arte, incrível!",
    "Compre o álbum agora e ganhe um desconto!",
    "A voz da cantora é única, apaixonante.",
    "O som do show estava ótimo, curti muito.",
    "Seria interessante ter mais colaborações.",
    "Qual é a história por trás do clipe?",
    "Clique aqui para ouvir o álbum completo!",
    "A produção do álbum é de alta qualidade, adorei!",
    "O clipe é muito bem feito, parabéns!",
    "Gostaria que lançassem mais remixes.",
    "Por que não há mais vídeos como esse?",
    "Visite nosso site para conteúdos exclusivos!",
    "A faixa 2 é minha favorita, viciei!",
    "Flop total de álbum, uma vergonha.",
    "Flopou o show, som ruim e luz fraca.",
    "A letra da música é rasa, esperava mais.",
    "Achei bafonico o novo álbum, hit atrás de hit!",
    "Muito divos, juro!",
    "A voz da cantora é icônica, amo demais!",
    "O som do show estava top, arrasaram!",
    "Seria mara ter mais músicas assim.",
    "Qual é a inspiração por trás do álbum?",
    "Compre já o álbum e arrase nas festas!",
    "Amei a vibe do clipe, sensacional!",
    "O álbum é bafônico, lacrou demais!",
    "Show hino, melhor que o anterior!",
    "A letra da música é hit, não paro de ouvir.",
    "Promoção imperdível: compre 1, leve 3!",
    "A voz ao vivo é maravilhosa, perfeita!",
    "O som estava icônico, arrasaram no show.",
    "Poderia ter mais hinos no próximo álbum.",
    "Onde posso encontrar os hinos completos?",
    "Siga nosso perfil para mais hinos!"
]


def main() -> int:
    app = create_app()
    with app.app_context():
        created = 0
        for texto in SAMPLE_COMMENTS:
            result = classificar_texto(texto)
            c = Comentario(
                texto=texto,
                categoria=result.get("categoria"),
                tags_funcionalidades=result.get("tags_funcionalidades"),
                confianca=result.get("confianca"),
            )
            db.session.add(c)
            created += 1
        db.session.commit()
        print(f"Seeded {created} comments.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

