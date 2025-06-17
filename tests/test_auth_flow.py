import pytest
from flask import Flask
import responses

from core.auth import init_auth


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("AUTH0_CLIENT_ID", "cid")
    monkeypatch.setenv("AUTH0_CLIENT_SECRET", "secret")
    monkeypatch.setenv("AUTH0_DOMAIN", "auth.example.com")
    monkeypatch.setenv("AUTH0_AUDIENCE", "aud")
    app = Flask(__name__)
    app.secret_key = "test"
    init_auth(app)
    return app.test_client()


@responses.activate
def test_login_redirect(client):
    responses.add(
        responses.GET,
        "https://auth.example.com/.well-known/openid-configuration",
        json={
            "authorization_endpoint": "https://auth.example.com/authorize",
            "token_endpoint": "https://auth.example.com/oauth/token",
            "jwks_uri": "https://auth.example.com/.well-known/jwks.json",
        },
    )
    resp = client.get("/login")
    assert resp.status_code == 302
    assert "auth.example.com/authorize" in resp.headers["Location"]
