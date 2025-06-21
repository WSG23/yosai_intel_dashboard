"""
File Upload Plugin
Consolidates file uploader UI and processing into a single plugin.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from core.plugins.protocols import CallbackPluginProtocol, PluginMetadata, PluginPriority

# Reuse existing uploader UI and processing logic
try:
    from components.analytics.file_uploader import (
        create_dual_file_uploader as _create_dual_file_uploader,
        register_dual_upload_callbacks as _register_dual_upload_callbacks,
    )
    from components.analytics.file_processing import FileProcessor as _FileProcessor
    COMPONENTS_AVAILABLE = True
except Exception as exc:  # pragma: no cover - optional dependency handling
    logging.getLogger(__name__).warning(
        "File upload components unavailable: %s", exc
    )
    COMPONENTS_AVAILABLE = False
    _create_dual_file_uploader = None
    _register_dual_upload_callbacks = None
    _FileProcessor = None

def create_dual_file_uploader(upload_id: str = "analytics-file-upload"):
    """Safe wrapper to create the file uploader component."""
    if COMPONENTS_AVAILABLE and _create_dual_file_uploader:
        return _create_dual_file_uploader(upload_id)
    try:
        from dash import html
        return html.Div("File uploader component not available")
    except Exception:
        return None


def register_dual_upload_callbacks(app: Any, upload_id: str = "analytics-file-upload") -> bool:
    """Safely register upload callbacks if components are available."""
    if COMPONENTS_AVAILABLE and _register_dual_upload_callbacks:
        try:
            _register_dual_upload_callbacks(app, upload_id)
            return True
        except Exception as exc:  # pragma: no cover - runtime failure
            logging.getLogger(__name__).error("Failed to register callbacks: %s", exc)
            return False
    return False


FileProcessor = _FileProcessor  # type: ignore


@dataclass
class FileUploadConfig:
    """Configuration options for the file upload plugin."""

    enabled: bool = True
    allow_database_connections: bool = False
    database_uri: Optional[str] = None


class FileUploadPlugin(CallbackPluginProtocol):
    """Plugin providing file upload components and processing."""

    _metadata = PluginMetadata(
        name="FileUploadPlugin",
        version="1.0",
        description="Provide CSV/JSON/XLS upload and processing",
        author="Yosai",
        priority=PluginPriority.NORMAL,
    )

    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return self._metadata

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.config = FileUploadConfig()
        self._started = False

    # Plugin lifecycle --------------------------------------------------
    def load(self, container: Any, config: Dict[str, Any]) -> bool:
        """Load the plugin and register services."""
        try:
            if config:
                self.configure(config)
            if container and hasattr(container, "register"):
                container.register("file_processor", FileProcessor)
            return True
        except Exception as exc:
            self.logger.error("FileUploadPlugin load failed: %s", exc)
            return False

    def configure(self, config: Dict[str, Any]) -> bool:
        """Configure plugin settings."""
        try:
            for key, value in (config or {}).items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            return True
        except Exception as exc:
            self.logger.error("FileUploadPlugin configure failed: %s", exc)
            return False

    def start(self) -> bool:
        self._started = True
        return True

    def stop(self) -> bool:
        self._started = False
        return True

    def health_check(self) -> Dict[str, Any]:
        return {
            "healthy": True,
            "started": self._started,
            "database_connected": bool(self.config.database_uri),
        }

    # Database ----------------------------------------------------------
    def connect_database(self, uri: str) -> bool:
        """Placeholder for future database integration."""
        self.config.database_uri = uri
        return True

    # Component creation ------------------------------------------------
    def create_dual_file_uploader(self, upload_id: str = "analytics-file-upload"):
        """Create dual file uploader through plugin"""
        if COMPONENTS_AVAILABLE and _create_dual_file_uploader:
            return _create_dual_file_uploader(upload_id)
        try:
            from dash import html
            return html.Div("File uploader component not available", className="alert alert-warning")
        except Exception:
            return None

    # Callback registration --------------------------------------------
    def register_callbacks(self, app: Any, container: Any) -> bool:
        try:
            register_dual_upload_callbacks(app, "file-upload-main")
            return True
        except Exception as exc:
            self.logger.error("Failed to register upload callbacks: %s", exc)
            return False


# Convenience wrappers -------------------------------------------------

def create_file_uploader(upload_id: str = "analytics-file-upload"):
    """Backward compatible wrapper for dual file uploader."""
    return create_dual_file_uploader(upload_id)


__all__ = [
    "create_file_uploader",
    "create_dual_file_uploader",
    "register_dual_upload_callbacks",
    "FileProcessor",
    "FileUploadPlugin",
    "create_plugin",
]


def create_plugin() -> FileUploadPlugin:
    """Factory used by the plugin manager."""
    return FileUploadPlugin()

