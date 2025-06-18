"""Simple cache manager implementation used for dependency injection."""

from typing import Any, Dict


class CacheManager:
    """Minimal in-memory cache manager."""

    def __init__(self, config: Any) -> None:
        self.config = config
        self._cache: Dict[str, Any] = {}

    @classmethod
    def from_config(cls, config: Any) -> "CacheManager":
        """Factory method used by :mod:`core.service_registry`."""
        return cls(config)

    def get(self, key: str) -> Any:
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = value

    def delete(self, key: str) -> None:
        self._cache.pop(key, None)

    def clear(self) -> None:
        self._cache.clear()


__all__ = ["CacheManager"]

