def test_container_isolation():
    from core.unified_container import UnifiedServiceContainer

    container = UnifiedServiceContainer()
    container.register_singleton('test', lambda: "singleton_value")

    assert container.get('test') == "singleton_value"
    assert container.get('test') is container.get('test')


def test_config_loading():
    from config.unified_config import ConfigurationLoader

    loader = ConfigurationLoader()
    config = loader.load_config('development')

    assert config.database.type in ['sqlite', 'postgresql', 'mock']
    assert config.app.environment == 'development'
