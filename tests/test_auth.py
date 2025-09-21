def test_login_jwt(client):
    #login JWT usa credenciais fixas do auth.py (admin/123)
    res = client.post('/auth/login', json={'username': 'admin', 'password': '123'})
    assert res.status_code == 200
    data = res.get_json()
    assert 'access_token' in data

