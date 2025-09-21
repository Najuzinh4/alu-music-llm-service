from datetime import datetime, timedelta

from app.models import db, WeeklySummary


def _jwt_token(client):
    res = client.post('/auth/login', json={'username': 'admin', 'password': '123'})
    return res.get_json()['access_token']


def test_insights_perguntar(client):
    with client.application.app_context():
        # cria 3 resumos recentes
        now = datetime.utcnow()
        for i in range(3):
            db.session.add(WeeklySummary(week=f"2025-W{30+i}", content=f"Resumo {i}"))
        db.session.commit()

    token = _jwt_token(client)
    res = client.post('/insights/perguntar', json={'pergunta': 'Quais tendências?'}, headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    data = res.get_json()
    assert 'resposta' in data and 'semanas' in data
    assert len(data['semanas']) >= 1

