"""Service access helpers for Yōsai Intel Dashboard."""

from services.service_registry import register_all_services, get_service as _get_service

_services_initialized = False


def _ensure_services() -> None:
    global _services_initialized
    if not _services_initialized:
        register_all_services()
        _services_initialized = True


def get_service(name: str):
    """Retrieve a service from the global container."""
    _ensure_services()
    return _get_service(name)


__all__ = ["get_service"]

