from app import routes as api_routes


def test_post_comentarios_with_classification_mock(client, monkeypatch):
    #obtem token JWT
    res_login = client.post('/auth/login', json={'username': 'admin', 'password': '123'})
    token = res_login.get_json()['access_token']

    #isso é o mock da função de classificação para resultado determinístico
    def fake_classificar_texto(texto: str):
        return {
            'categoria': 'ELOGIO',
            'tags_funcionalidades': [{'code': 'feat_autotune', 'explanation': 'ok'}],
            'confianca': 0.99,
        }

    monkeypatch.setattr(api_routes, 'classificar_texto', fake_classificar_texto, raising=False)

    payload = {'texto': 'amei o clipe!'}
    res = client.post('/api/comentarios', json=payload, headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 201
    data = res.get_json()
    assert isinstance(data, list) and len(data) == 1
    rec = data[0]
    assert rec['categoria'] == 'ELOGIO'
    assert rec['confianca'] == 0.99
    assert rec['tags_funcionalidades'][0]['code'] == 'feat_autotune'

