from typing import Any
from .lazystring_utils import sanitize_json_data


def sanitize_lazystring_recursive(data: Any) -> Any:
    """Recursively convert LazyString objects to plain strings."""
    return sanitize_json_data(data)

__all__ = ["sanitize_lazystring_recursive"]
