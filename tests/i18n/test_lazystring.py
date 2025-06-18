import pytest

from core.app_factory import create_application_for_testing

@pytest.mark.i18n
def test_lazystring_response_converted():
    app = create_application_for_testing()
    assert app is not None
    server = app.server
    with server.test_client() as client:
        resp = client.get('/api/ping')
        assert resp.status_code == 200
        assert resp.get_json()['msg'] == 'pong'
