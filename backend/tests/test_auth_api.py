"""Testes de integração do fluxo de autenticação via API."""


def _register(client, email="user@test.com", password="segredo123"):
    return client.post(
        "/auth/register",
        json={"email": email, "password": password, "full_name": "Teste"},
    )


def test_register_cria_usuario(client):
    resp = _register(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "user@test.com"
    assert "hashed_password" not in body  # nunca vazar o hash.


def test_register_email_duplicado_falha(client):
    _register(client)
    resp = _register(client)
    assert resp.status_code == 409


def test_login_retorna_token(client):
    _register(client)
    resp = client.post(
        "/auth/login",
        data={"username": "user@test.com", "password": "segredo123"},
    )
    assert resp.status_code == 200
    assert resp.json()["token_type"] == "bearer"
    assert resp.json()["access_token"]


def test_login_senha_errada_401(client):
    _register(client)
    resp = client.post(
        "/auth/login",
        data={"username": "user@test.com", "password": "errada"},
    )
    assert resp.status_code == 401


def test_me_exige_token(client):
    assert client.get("/auth/me").status_code == 401


def test_me_com_token_retorna_usuario(client):
    _register(client)
    token = client.post(
        "/auth/login",
        data={"username": "user@test.com", "password": "segredo123"},
    ).json()["access_token"]

    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "user@test.com"


def test_chat_sem_token_bloqueado(client):
    # Rota protegida: sem credencial -> 401, sem nem chegar no LLM/banco.
    resp = client.post("/chat", json={"question": "Quantos pedidos existem?"})
    assert resp.status_code == 401
