import importlib
import pkgutil
import logging
from typing import List, Any

from core.container import Container
from config.yaml_config import ConfigurationManager

logger = logging.getLogger(__name__)

class PluginManager:
    """Simple plugin manager that loads plugins from the 'plugins' package."""

    def __init__(self, container: Container, config_manager: ConfigurationManager, package: str = "plugins"):
        self.container = container
        self.config_manager = config_manager
        self.package = package
        self.loaded_plugins: List[Any] = []

    def load_all_plugins(self) -> List[Any]:
        """Dynamically load all plugins from the configured package."""
        try:
            pkg = importlib.import_module(self.package)
        except ModuleNotFoundError:
            logger.info("Plugins package '%s' not found", self.package)
            return []

        results = []
        for loader, name, is_pkg in pkgutil.iter_modules(pkg.__path__):
            module_name = f"{self.package}.{name}"
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, "init_plugin"):
                    result = module.init_plugin(self.container, self.config_manager)
                    results.append(result)
                self.loaded_plugins.append(module)
                logger.info("Loaded plugin %s", module_name)
            except Exception as exc:
                logger.error("Failed to load plugin %s: %s", module_name, exc)
        return results
