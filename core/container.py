"""Service access helpers for Yōsai Intel Dashboard."""

from core.unified_container import UnifiedServiceContainer, get_container


class Container(UnifiedServiceContainer):
    """Backward-compatible container alias"""


def get_service(name: str):
    """Retrieve a service from the global container."""
    container = get_container()
    return container.get(name)


__all__ = ["get_service", "Container", "get_container"]

