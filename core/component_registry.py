#!/usr/bin/env python3
"""Component registry integrated with DI container"""
from typing import Any, Optional, Dict
import logging
from utils.safe_components import get_safe_component

logger = logging.getLogger(__name__)


class ComponentRegistry:
    """Component registry integrated with dependency injection"""

    def __init__(self, container=None):
        self.container = container
        self._component_factories: Dict[str, str] = {}
        self._fallback_components: Dict[str, Any] = {}
        self._register_component_services()

    def _register_component_services(self) -> None:
        """Register component factories with the DI container"""
        if not self.container:
            logger.warning("No DI container available - using fallback mode")
            return

        try:
            # Register component factories as services
            self._register_navbar_service()
            self._register_panel_services()
            self._register_callback_services()

        except Exception as e:
            logger.error(f"Error registering component services: {e}")

    def _register_navbar_service(self) -> None:
        """Register navbar as a service"""
        try:
            def navbar_factory():
                from dashboard.layout.navbar import create_navbar_layout
                return create_navbar_layout()

            self.container.register(
                'navbar_component',
                navbar_factory,
                singleton=True
            )
            logger.info("Navbar service registered")
        except Exception as e:
            logger.error(f"Failed to register navbar service: {e}")

    def _register_panel_services(self) -> None:
        """Register panel components as services"""
        panel_configs = [
            ('incident_alerts_component', 'components.incident_alerts_panel', 'layout'),
            ('map_panel_component', 'components.map_panel', 'layout'),
            ('bottom_panel_component', 'components.bottom_panel', 'layout'),
            ('weak_signal_component', 'components.weak_signal_panel', 'layout'),
        ]

        for service_name, module_name, function_name in panel_configs:
            try:
                def create_factory(mod_name, func_name):
                    def factory():
                        try:
                            module = __import__(mod_name, fromlist=[func_name])
                            component_func = getattr(module, func_name, None)
                            if component_func and callable(component_func):
                                return component_func()
                            return None
                        except Exception as e:
                            logger.error(f"Error creating {service_name}: {e}")
                            return None
                    return factory

                self.container.register(
                    service_name,
                    create_factory(module_name, function_name),
                    singleton=True
                )
                logger.info(f"Panel service registered: {service_name}")

            except Exception as e:
                logger.error(f"Failed to register {service_name}: {e}")

    def _register_callback_services(self) -> None:
        """Register callback registration functions as services"""
        try:
            # Register analytics module through DI container
            def analytics_factory():
                try:
                    import pages.deep_analytics as analytics_module
                    return analytics_module
                except ImportError:
                    return None

            self.container.register(
                'analytics_module',
                analytics_factory,
                singleton=True
            )

        except Exception as e:
            logger.error(f"Failed to register callback services: {e}")

    def get_component_or_fallback(self, name: str, fallback_message: str = None) -> Any:
        """Get component from DI container or return safe fallback"""
        if not self.container:
            return get_safe_component(name)

        # Map component names to service names
        service_mapping = {
            'navbar': 'navbar_component',
            'incident_alerts': 'incident_alerts_component',
            'map_panel': 'map_panel_component',
            'bottom_panel': 'bottom_panel_component',
            'weak_signal': 'weak_signal_component',
            'analytics_module': 'analytics_module'
        }

        service_name = service_mapping.get(name)
        if not service_name:
            logger.warning(f"No service mapping for component: {name}")
            return get_safe_component(name)

        try:
            # Get component from DI container
            component = self.container.get(service_name)
            if component is not None:
                return component
            else:
                logger.warning(f"Service {service_name} returned None, using fallback")
                return get_safe_component(name)

        except Exception as e:
            logger.error(f"Error getting component {name} from container: {e}")
            return get_safe_component(name)

    def get_component(self, name: str) -> Optional[Any]:
        """Get component without fallback"""
        if not self.container:
            return None

        service_mapping = {
            'analytics_module': 'analytics_module',
            'map_panel_callbacks': 'map_panel_component',
            'navbar_callbacks': 'navbar_component'
        }

        service_name = service_mapping.get(name)
        if service_name:
            try:
                return self.container.get(service_name)
            except:
                return None
        return None
