# tests/test_json_serialization_plugin.py
"""
Comprehensive tests for the JSON Serialization Plugin
"""
import pytest
pytest.importorskip("pandas")

import unittest
import pandas as pd
from datetime import datetime
import json

from plugins.builtin.json_serialization_plugin import (
    JsonSerializationPlugin, JsonSerializationConfig,
    JsonSerializationService, JsonCallbackService
)
from core.plugins.manager import PluginManager
from core.container import Container as DIContainer

class TestJsonSerializationPlugin(unittest.TestCase):
    """Test the JSON Serialization Plugin"""
    
    def setUp(self):
        self.plugin = JsonSerializationPlugin()
        self.container = DIContainer()
        self.config = {
            'enabled': True,
            'max_dataframe_rows': 5,
            'auto_wrap_callbacks': True
        }
    
    def test_plugin_metadata(self):
        """Test plugin metadata"""
        metadata = self.plugin.metadata
        
        self.assertEqual(metadata.name, 'json_serialization')
        self.assertEqual(metadata.version, '1.0.0')
        self.assertTrue(metadata.enabled_by_default)
    
    def test_plugin_lifecycle(self):
        """Test plugin load, configure, start, stop lifecycle"""
        # Load
        success = self.plugin.load(self.container, self.config)
        self.assertTrue(success)
        
        # Configure
        success = self.plugin.configure(self.config)
        self.assertTrue(success)
        
        # Start
        success = self.plugin.start()
        self.assertTrue(success)
        
        # Health check
        health = self.plugin.health_check()
        self.assertTrue(health['healthy'])
        
        # Stop
        success = self.plugin.stop()
        self.assertTrue(success)
    
    def test_service_registration(self):
        """Test that services are properly registered"""
        self.plugin.load(self.container, self.config)
        
        # Check that services are registered
        self.assertTrue(self.container.has('json_serialization_service'))
        self.assertTrue(self.container.has('json_callback_service'))
        
        # Test service functionality
        serialization_service = self.container.get('json_serialization_service')
        self.assertIsNotNone(serialization_service)
        
        # Test DataFrame serialization
        df = pd.DataFrame({'A': [1, 2, 3], 'B': ['x', 'y', 'z']})
        result = serialization_service.sanitize_for_transport(df)
        
        self.assertEqual(result['type'], 'dataframe')
        self.assertEqual(result['shape'], (3, 2))
        self.assertEqual(len(result['data']), 3)
    
    def test_callback_wrapping(self):
        """Test callback function wrapping"""
        self.plugin.load(self.container, self.config)
        
        callback_service = self.container.get('json_callback_service')
        
        def test_callback():
            return pd.DataFrame({'A': [1, 2, 3]})
        
        wrapped_callback = callback_service.wrap_callback(test_callback)
        result = wrapped_callback()
        
        # Should return sanitized DataFrame representation
        self.assertIsInstance(result, dict)
        self.assertEqual(result['type'], 'dataframe')
    
    def test_error_handling(self):
        """Test error handling in callbacks"""
        self.plugin.load(self.container, self.config)
        
        callback_service = self.container.get('json_callback_service')
        
        def failing_callback():
            raise ValueError("Test error")
        
        wrapped_callback = callback_service.wrap_callback(failing_callback)
        result = wrapped_callback()
        
        # Should return error representation
        self.assertTrue(result.get('error', False))
        self.assertIn('Test error', result['message'])

    def test_lazystring_handling(self):
        """Ensure LazyString objects are sanitized to plain strings"""
        try:
            from flask_babel import lazy_gettext
        except Exception:
            self.skipTest("flask_babel not available")

        self.plugin.load(self.container, self.config)
        service = self.container.get('json_serialization_service')

        lazy_value = lazy_gettext("hello")
        sanitized = service.sanitize_for_transport(lazy_value)

        self.assertIsInstance(sanitized, str)
        self.assertEqual(sanitized, str(lazy_value))

class TestPluginManager(unittest.TestCase):
    """Test plugin manager with JSON serialization plugin"""
    
    def setUp(self):
        self.container = Container()
        self.manager = PluginManager(self.container)
    
    def test_plugin_discovery(self):
        """Test that the JSON serialization plugin can be discovered"""
        # This test would require the plugin to be in the discovery path
        # For now, we test manual plugin loading
        
        plugin = JsonSerializationPlugin()
        success = self.manager.load_plugin(plugin)
        
        self.assertTrue(success)
        self.assertIn('json_serialization', self.manager.plugins)
    
    def test_plugin_health_monitoring(self):
        """Test plugin health monitoring"""
        plugin = JsonSerializationPlugin()
        self.manager.load_plugin(plugin)
        
        health_status = self.manager.get_plugin_health()
        
        self.assertIn('json_serialization', health_status)
        self.assertTrue(health_status['json_serialization']['health']['healthy'])

if __name__ == '__main__':
    unittest.main()
