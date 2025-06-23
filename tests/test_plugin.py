"""
Comprehensive tests for the CSRF protection plugin
"""

import pytest
import os
import dash
from dash import html, dcc, Input, Output
from unittest.mock import patch, MagicMock
from flask import Flask

from dash_csrf_plugin import (
    DashCSRFPlugin,
    CSRFConfig,
    CSRFMode,
    CSRFError,
    CSRFConfigurationError,
)


class TestCSRFConfig:
    """Test CSRF configuration functionality"""

    def test_default_config(self):
        config = CSRFConfig(secret_key="test")
        assert config.enabled is True
        assert config.time_limit == 3600
        assert config.ssl_strict is True
        assert 'POST' in config.methods

    def test_development_config(self):
        config = CSRFConfig.for_development()
        assert config.enabled is False
        assert config.ssl_strict is False
        assert config.secret_key == 'change-me'

    def test_production_config(self):
        config = CSRFConfig.for_production('production-secret')
        assert config.enabled is True
        assert config.ssl_strict is True
        assert config.secret_key == 'production-secret'

    def test_testing_config(self):
        config = CSRFConfig.for_testing()
        assert config.enabled is False
        assert config.secret_key == 'test-secret-key'

    def test_from_environment(self, monkeypatch):
        env_vars = {
            'CSRF_ENABLED': 'true',
            'CSRF_SECRET_KEY': 'env-secret',
            'CSRF_TIME_LIMIT': '1800',
            'CSRF_SSL_STRICT': 'false',
        }
        monkeypatch.setenv('CSRF_ENABLED', 'true')
        monkeypatch.setenv('CSRF_SECRET_KEY', 'env-secret')
        monkeypatch.setenv('CSRF_TIME_LIMIT', '1800')
        monkeypatch.setenv('CSRF_SSL_STRICT', 'false')
        config = CSRFConfig.from_environment()
        assert config.enabled is True
        assert config.secret_key == 'env-secret'
        assert config.time_limit == 1800
        assert config.ssl_strict is False

    def test_config_validation(self):
        with pytest.raises(ValueError):
            CSRFConfig(enabled=True, secret_key=None)
        with pytest.raises(ValueError):
            CSRFConfig(time_limit=0, secret_key="x")

    def test_config_to_dict(self):
        config = CSRFConfig(secret_key='test-secret')
        config_dict = config.to_dict()
        assert 'enabled' in config_dict
        assert config_dict['secret_key'] == '***'
        assert config_dict['time_limit'] == 3600


class TestDashCSRFPlugin:
    @pytest.fixture
    def dash_app(self):
        app = dash.Dash(__name__)
        app.server.config['SECRET_KEY'] = 'test-secret'
        return app

    def test_plugin_creation(self, dash_app):
        plugin = DashCSRFPlugin()
        assert plugin.app is None
        assert not plugin._initialized

    def test_plugin_initialization(self, dash_app):
        plugin = DashCSRFPlugin(dash_app, mode=CSRFMode.TESTING)
        assert plugin.app == dash_app
        assert plugin._initialized
        assert plugin.mode == CSRFMode.TESTING

    def test_auto_mode_detection(self, dash_app):
        dash_app.server.config['DEBUG'] = True
        plugin = DashCSRFPlugin(dash_app, mode=CSRFMode.AUTO)
        assert plugin.mode == CSRFMode.DEVELOPMENT
        dash_app.server.config['DEBUG'] = False
        plugin = DashCSRFPlugin(mode=CSRFMode.AUTO)
        plugin.init_app(dash_app)
        assert plugin.mode == CSRFMode.PRODUCTION

    def test_exempt_routes(self, dash_app):
        plugin = DashCSRFPlugin(dash_app, mode=CSRFMode.TESTING)
        plugin.add_exempt_route('/custom-route')
        assert '/custom-route' in plugin.manager._exempt_routes
        assert '/_dash-dependencies' in plugin.manager._exempt_routes

    def test_exempt_route_calls_csrf_exempt(self, dash_app):
        plugin = DashCSRFPlugin(dash_app, mode=CSRFMode.ENABLED)
        plugin.manager.csrf_protect = MagicMock()

        # Create a fake rule so the manager can locate the view function
        rule = MagicMock()
        rule.rule = '/custom'
        rule.endpoint = 'custom_endpoint'
        dash_app.server.url_map.iter_rules = MagicMock(return_value=[rule])
        dash_app.server.view_functions['custom_endpoint'] = lambda: 'ok'

        plugin.add_exempt_route('/custom')
        plugin.manager.csrf_protect.exempt.assert_called_once()

    def test_csrf_token_generation(self, dash_app):
        plugin = DashCSRFPlugin(dash_app, mode=CSRFMode.ENABLED)
        with dash_app.server.app_context():
            with patch('dash_csrf_plugin.manager.generate_csrf') as mock_generate:
                mock_generate.return_value = 'test-token'
                token = plugin.get_csrf_token()
                assert token == 'test-token'

    def test_csrf_component_creation(self, dash_app):
        plugin = DashCSRFPlugin(dash_app, mode=CSRFMode.TESTING)
        component = plugin.create_csrf_component()
        assert component is not None

    def test_plugin_status(self, dash_app):
        plugin = DashCSRFPlugin(dash_app, mode=CSRFMode.TESTING)
        status = plugin.get_status()
        assert 'initialized' in status
        assert 'mode' in status
        assert status['initialized'] is True
        assert status['mode'] == 'testing'

    def test_plugin_hooks(self, dash_app):
        plugin = DashCSRFPlugin(dash_app, mode=CSRFMode.TESTING)
        hook_called = False

        def test_hook():
            nonlocal hook_called
            hook_called = True

        plugin.add_hook('before_init', test_hook)
        assert len(plugin._hooks['before_init']) == 1
        plugin._run_hooks('before_init')
        assert hook_called

    def test_configuration_error(self):
        invalid_app = MagicMock()
        if hasattr(invalid_app, 'server'):
            del invalid_app.server
        with pytest.raises(CSRFConfigurationError):
            DashCSRFPlugin(invalid_app)


class TestCSRFIntegration:
    @pytest.fixture
    def app_with_csrf(self):
        app = dash.Dash(__name__)
        app.server.config['SECRET_KEY'] = 'test-secret'
        plugin = DashCSRFPlugin(app, mode=CSRFMode.TESTING)
        app.layout = html.Div([
            plugin.create_csrf_component(),
            html.Button('Test', id='test-btn', n_clicks=0),
            html.Div(id='output')
        ])

        @app.callback(Output('output', 'children'), Input('test-btn', 'n_clicks'))
        def update_output(n_clicks):
            return f'Clicks: {n_clicks}'
        return app, plugin

    def test_app_loads_successfully(self, app_with_csrf):
        app, plugin = app_with_csrf
        with app.server.test_client() as client:
            response = client.get('/')
            assert response.status_code == 200

    def test_health_endpoint(self, app_with_csrf):
        app, plugin = app_with_csrf
        with app.server.test_client() as client:
            response = client.get('/health')
            assert response.status_code == 200

    def test_csrf_disabled_in_testing(self, app_with_csrf):
        app, plugin = app_with_csrf
        assert not plugin.is_enabled
        assert app.server.config.get('WTF_CSRF_ENABLED') is False


class TestCSRFModes:
    def test_development_mode(self):
        app = dash.Dash(__name__)
        app.server.config['SECRET_KEY'] = 'test'
        plugin = DashCSRFPlugin(app, mode=CSRFMode.DEVELOPMENT)
        assert not plugin.is_enabled
        assert app.server.config.get('WTF_CSRF_ENABLED') is False

    def test_production_mode(self):
        app = dash.Dash(__name__)
        app.server.config['SECRET_KEY'] = 'test'
        plugin = DashCSRFPlugin(app, mode=CSRFMode.PRODUCTION)
        assert plugin.is_enabled
        assert app.server.config.get('WTF_CSRF_ENABLED') is True

    def test_disabled_mode(self):
        app = dash.Dash(__name__)
        app.server.config['SECRET_KEY'] = 'test'
        plugin = DashCSRFPlugin(app, mode=CSRFMode.DISABLED)
        assert not plugin.is_enabled
        assert app.server.config.get('WTF_CSRF_ENABLED') is False
