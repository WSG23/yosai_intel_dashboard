"""Dependency injection container tests"""
import pytest
from core.container import Container, TestContainer

class TestDependencyInjection:
    def test_container_factory_registration(self):
        container = Container()
        def create_service():
            return "test_service"
        container.register_factory('test', create_service)
        service = container.get('test')
        assert service == "test_service"

    def test_container_singleton_registration(self):
        container = Container()
        call_count = 0
        def create_singleton():
            nonlocal call_count
            call_count += 1
            return f"singleton_{call_count}"
        container.register_singleton('singleton', create_singleton)
        service1 = container.get('singleton')
        service2 = container.get('singleton')
        assert service1 == service2
        assert call_count == 1

    def test_container_instance_registration(self):
        container = Container()
        instance = {"data": "test"}
        container.register_instance('instance', instance)
        retrieved = container.get('instance')
        assert retrieved is instance

    def test_container_missing_service(self):
        container = Container()
        with pytest.raises(KeyError):
            container.get('nonexistent')

    def test_test_container_context_manager(self):
        with TestContainer() as test_container:
            test_container.register_instance('test', 'value')
            assert test_container.get('test') == 'value'
