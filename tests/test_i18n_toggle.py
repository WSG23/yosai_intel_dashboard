import pytest
from core.app_factory import create_application_for_testing


def test_i18n_toggle_route_sets_session():
    app = create_application_for_testing()
    assert app is not None
    server = app.server
    with server.test_client() as client:
        response = client.get("/i18n/ja", follow_redirects=False)
        assert response.status_code == 302
        with client.session_transaction() as sess:
            assert sess.get("lang") == "ja"
