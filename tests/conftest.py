"""
Pytest configuration for CSRF plugin tests
"""

import pytest
import dash
from dash_csrf_plugin import DashCSRFPlugin, CSRFConfig, CSRFMode


@pytest.fixture(scope="session")
def test_config():
    return CSRFConfig.for_testing()


@pytest.fixture
def dash_app():
    app = dash.Dash(__name__)
    app.server.config.update({
        'SECRET_KEY': 'test-secret-key',
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
    })
    return app


@pytest.fixture
def csrf_plugin(dash_app, test_config):
    return DashCSRFPlugin(dash_app, config=test_config, mode=CSRFMode.TESTING)


@pytest.fixture
def client(dash_app):
    return dash_app.server.test_client()
