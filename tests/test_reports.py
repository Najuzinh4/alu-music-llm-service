from datetime import datetime, timedelta

from app.models import db, Comentario


def test_weekly_report_json(client):
    # Seed mínimo
    with client.application.app_context():
        db.session.add(Comentario(texto="amei o álbum", categoria="ELOGIO", confianca=0.9))
        db.session.add(Comentario(texto="clipe ruim", categoria="CRÍTICA", confianca=0.7))
        db.session.commit()

    res = client.get('/relatorio/semana?format=json')
    assert res.status_code == 200
    data = res.get_json()
    assert 'charts' in data and isinstance(data['charts'], dict)
    assert any(k in data['charts'] for k in ['volume_dia','categorias'])

