"""Compatibility configuration package."""
from importlib import import_module

# Lazy modules pointing to new location
_yaml = import_module('core.plugins.config.yaml_config')
_database = import_module('core.plugins.config.database_manager')
_cache = import_module('core.plugins.config.cache_manager')

__all__ = []  # will extend below

# Re-export top-level names from submodules for backward compatibility
for _mod in (_yaml, _database, _cache):
    globals().update({k: getattr(_mod, k) for k in getattr(_mod, '__all__', [])})
    __all__.extend(getattr(_mod, '__all__', []))

