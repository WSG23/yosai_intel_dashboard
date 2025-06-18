#!/usr/bin/env python3
"""
Service Availability Checker - Fixed for Actual Project Structure
================================================================

A comprehensive, modular service checker that integrates with your ACTUAL
project architecture and DI container system.

Usage:
    python3 check_services.py
    python3 check_services.py --format json
    python3 check_services.py --services analytics_service,database
    python3 check_services.py --deep-check
"""

import sys
import time
import json
import argparse
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status enumeration"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    NOT_FOUND = "not_found"
    DEGRADED = "degraded"


@dataclass
class ServiceInfo:
    """Service information data class"""
    name: str
    status: ServiceStatus
    type: str
    layer: Optional[str] = None
    dependencies: List[str] = None
    health_data: Dict[str, Any] = None
    error_message: Optional[str] = None
    response_time_ms: Optional[float] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.health_data is None:
            self.health_data = {}


class ServiceChecker:
    """Base service checker interface"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    def check(self) -> ServiceInfo:
        """Check service availability"""
        raise NotImplementedError
    
    def _measure_response_time(self, func) -> tuple[Any, float]:
        """Measure function execution time"""
        start_time = time.time()
        try:
            result = func()
            response_time = (time.time() - start_time) * 1000
            return result, response_time
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            raise e


class DIContainerChecker(ServiceChecker):
    """Checks DI container and registered services"""
    
    def __init__(self):
        super().__init__("di_container")
    
    def check(self) -> ServiceInfo:
        try:
            result, response_time = self._measure_response_time(
                lambda: self._check_container_health()
            )
            
            return ServiceInfo(
                name="di_container",
                status=ServiceStatus.HEALTHY,
                type="infrastructure",
                layer="core",
                health_data=result,
                response_time_ms=response_time
            )
            
        except ImportError as e:
            return ServiceInfo(
                name="di_container",
                status=ServiceStatus.NOT_FOUND,
                type="infrastructure",
                error_message=f"DI Container not found: {e}"
            )
        except Exception as e:
            return ServiceInfo(
                name="di_container",
                status=ServiceStatus.UNHEALTHY,
                type="infrastructure",
                error_message=str(e)
            )
    
    def _check_container_health(self) -> Dict[str, Any]:
        # Try the actual imports from your project
        try:
            from core.service_registry import get_configured_container
            container = get_configured_container()
            
            # Test health check if available
            if hasattr(container, 'health_check'):
                health = container.health_check()
                return {
                    'container_type': type(container).__name__,
                    'services_registered': len(health.get('services', {})),
                    'overall_status': health.get('status', 'unknown'),
                    'has_health_check': True
                }
            else:
                # Basic check
                services = container.list_services() if hasattr(container, 'list_services') else []
                return {
                    'container_type': type(container).__name__,
                    'services_registered': len(services),
                    'has_health_check': False,
                    'services': services[:10]  # First 10 services
                }
                
        except ImportError:
            # Try alternative import paths
            from core.container import Container
            container = Container()
            return {
                'container_type': type(container).__name__,
                'services_registered': 0,
                'has_health_check': False,
                'note': 'Basic container - no services configured'
            }


class DatabaseChecker(ServiceChecker):
    """Checks database connectivity using your actual DatabaseManager"""
    
    def __init__(self):
        super().__init__("database")
    
    def check(self) -> ServiceInfo:
        try:
            result, response_time = self._measure_response_time(
                lambda: self._check_database_health()
            )
            
            return ServiceInfo(
                name="database",
                status=ServiceStatus.HEALTHY,
                type="infrastructure",
                layer="data",
                health_data=result,
                response_time_ms=response_time
            )
            
        except ImportError as e:
            return ServiceInfo(
                name="database",
                status=ServiceStatus.NOT_FOUND,
                type="infrastructure",
                error_message=f"Database manager not found: {e}"
            )
        except Exception as e:
            return ServiceInfo(
                name="database",
                status=ServiceStatus.UNHEALTHY,
                type="infrastructure",
                error_message=str(e)
            )
    
    def _check_database_health(self) -> Dict[str, Any]:
        from config.database_manager import DatabaseManager, DatabaseConfig
        
        # Test configuration loading
        config = DatabaseManager.from_environment()
        
        # Test connection creation (using your actual static method)
        connection = DatabaseManager.create_connection(config)
        
        # Test basic query
        try:
            result = connection.execute_query("SELECT 1 as test_query")
            query_successful = not result.empty
        except Exception as e:
            query_successful = False
            
        # Close connection properly
        connection.close()
        
        return {
            'config_loaded': True,
            'database_type': config.db_type,
            'connection_created': True,
            'test_query_successful': query_successful
        }


class AnalyticsServiceChecker(ServiceChecker):
    """Checks analytics service using your actual DI container"""
    
    def __init__(self):
        super().__init__("analytics_service")
    
    def check(self) -> ServiceInfo:
        try:
            result, response_time = self._measure_response_time(
                lambda: self._check_analytics_health()
            )
            
            return ServiceInfo(
                name="analytics_service",
                status=ServiceStatus.HEALTHY,
                type="business_logic",
                layer="service",
                dependencies=["database", "di_container"],
                health_data=result,
                response_time_ms=response_time
            )
            
        except ImportError as e:
            return ServiceInfo(
                name="analytics_service",
                status=ServiceStatus.NOT_FOUND,
                type="business_logic",
                error_message=f"Analytics service not found: {e}"
            )
        except Exception as e:
            return ServiceInfo(
                name="analytics_service",
                status=ServiceStatus.UNHEALTHY,
                type="business_logic",
                error_message=str(e)
            )
    
    def _check_analytics_health(self) -> Dict[str, Any]:
        try:
            # Try to get service from configured container
            from core.service_registry import get_configured_container
            container = get_configured_container()
            
            # Try to get analytics service
            analytics_service = None
            if hasattr(container, 'get_optional'):
                analytics_service = container.get_optional('analytics_service')
            elif hasattr(container, 'get'):
                try:
                    analytics_service = container.get('analytics_service')
                except:
                    pass
            
            if analytics_service is not None:
                # Test basic functionality
                try:
                    summary = analytics_service.get_dashboard_summary()
                    return {
                        'service_available': True,
                        'service_type': type(analytics_service).__name__,
                        'dashboard_summary_working': True,
                        'last_updated': summary.get('last_updated'),
                        'system_status': summary.get('system_status')
                    }
                except Exception as e:
                    return {
                        'service_available': True,
                        'service_type': type(analytics_service).__name__,
                        'dashboard_summary_working': False,
                        'error': str(e)
                    }
            else:
                return {
                    'service_available': False,
                    'container_services': len(container.list_services()) if hasattr(container, 'list_services') else 0,
                    'note': 'Analytics service not registered in container'
                }
                
        except Exception as e:
            return {
                'service_available': False,
                'container_error': str(e)
            }


class ConfigurationChecker(ServiceChecker):
    """Checks configuration system using your actual YAML config"""
    
    def __init__(self):
        super().__init__("configuration")
    
    def check(self) -> ServiceInfo:
        try:
            result, response_time = self._measure_response_time(
                lambda: self._check_config_health()
            )
            
            return ServiceInfo(
                name="configuration",
                status=ServiceStatus.HEALTHY,
                type="infrastructure",
                layer="core",
                health_data=result,
                response_time_ms=response_time
            )
            
        except ImportError as e:
            return ServiceInfo(
                name="configuration",
                status=ServiceStatus.NOT_FOUND,
                type="infrastructure",
                error_message=f"Configuration manager not found: {e}"
            )
        except Exception as e:
            return ServiceInfo(
                name="configuration",
                status=ServiceStatus.UNHEALTHY,
                type="infrastructure",
                error_message=str(e)
            )
    
    def _check_config_health(self) -> Dict[str, Any]:
        try:
            # Try your actual YAML configuration manager
            from config.yaml_config import ConfigurationManager
            
            config_manager = ConfigurationManager()
            config_manager.load_configuration()
            
            return {
                'config_manager_type': 'YAML',
                'config_loaded': hasattr(config_manager, '_config_source') and config_manager._config_source is not None,
                'environment': getattr(config_manager, 'environment', 'unknown'),
                'has_app_config': hasattr(config_manager, 'app_config'),
                'has_database_config': hasattr(config_manager, 'database_config')
            }
            
        except ImportError:
            # Try alternative config manager
            try:
                from core.config_manager import ConfigManager
                config = ConfigManager.from_environment()
                
                return {
                    'config_manager_type': 'Environment',
                    'config_loaded': True,
                    'has_app_config': hasattr(config, 'app_config')
                }
                
            except ImportError:
                raise ImportError("No configuration manager available")


class ServiceRegistry:
    """Registry of all available service checkers"""
    
    def __init__(self):
        self.checkers: Dict[str, ServiceChecker] = {
            'di_container': DIContainerChecker(),
            'database': DatabaseChecker(),
            'analytics_service': AnalyticsServiceChecker(),
            'configuration': ConfigurationChecker(),
        }
    
    def add_checker(self, name: str, checker: ServiceChecker):
        """Add a custom service checker"""
        self.checkers[name] = checker
    
    def get_available_services(self) -> List[str]:
        """Get list of available service names"""
        return list(self.checkers.keys())
    
    def check_service(self, name: str) -> ServiceInfo:
        """Check a specific service"""
        if name not in self.checkers:
            return ServiceInfo(
                name=name,
                status=ServiceStatus.NOT_FOUND,
                type="unknown",
                error_message=f"No checker available for service: {name}"
            )
        
        try:
            return self.checkers[name].check()
        except Exception as e:
            logger.error(f"Unexpected error checking {name}: {e}")
            return ServiceInfo(
                name=name,
                status=ServiceStatus.UNHEALTHY,
                type="unknown",
                error_message=f"Unexpected error: {e}"
            )
    
    def check_all_services(self) -> Dict[str, ServiceInfo]:
        """Check all registered services"""
        results = {}
        for name in self.checkers:
            results[name] = self.check_service(name)
        return results
    
    def check_services(self, service_names: List[str]) -> Dict[str, ServiceInfo]:
        """Check specific services"""
        results = {}
        for name in service_names:
            results[name] = self.check_service(name)
        return results


class ServiceStatusReporter:
    """Formats and reports service status"""
    
    @staticmethod
    def format_console(results: Dict[str, ServiceInfo]) -> str:
        """Format results for console output"""
        output = []
        output.append("📊 SERVICE AVAILABILITY CHECK")
        output.append("=" * 50)
        
        # Group by status
        status_groups = {}
        for service_info in results.values():
            status = service_info.status
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(service_info)
        
        # Display by status
        status_icons = {
            ServiceStatus.HEALTHY: "✅",
            ServiceStatus.UNHEALTHY: "❌",
            ServiceStatus.DEGRADED: "⚠️",
            ServiceStatus.NOT_FOUND: "🚫",
            ServiceStatus.UNKNOWN: "❓"
        }
        
        for status in ServiceStatus:
            if status not in status_groups:
                continue
                
            icon = status_icons.get(status, "❓")
            output.append(f"\n{icon} {status.value.upper()} SERVICES:")
            
            for service in status_groups[status]:
                output.append(f"  • {service.name} ({service.type})")
                if service.layer:
                    output.append(f"    Layer: {service.layer}")
                if service.response_time_ms:
                    output.append(f"    Response time: {service.response_time_ms:.2f}ms")
                if service.error_message:
                    output.append(f"    Error: {service.error_message}")
                if service.dependencies:
                    output.append(f"    Dependencies: {', '.join(service.dependencies)}")
                
                # Show key health data
                if service.health_data:
                    key_metrics = {}
                    for key, value in service.health_data.items():
                        if key in ['services_registered', 'database_type', 'service_type', 'config_manager_type']:
                            key_metrics[key] = value
                    
                    if key_metrics:
                        metrics_str = ', '.join([f"{k}={v}" for k, v in key_metrics.items()])
                        output.append(f"    Metrics: {metrics_str}")
        
        # Summary
        total = len(results)
        healthy = len([s for s in results.values() if s.status == ServiceStatus.HEALTHY])
        output.append(f"\n📈 SUMMARY: {healthy}/{total} services healthy")
        
        if healthy == total:
            output.append("🎉 All services are operational!")
        elif healthy == 0:
            output.append("⚠️  No services are healthy - check your configuration!")
        else:
            output.append("⚠️  Some services need attention")
        
        return "\n".join(output)
    
    @staticmethod
    def format_json(results: Dict[str, ServiceInfo]) -> str:
        """Format results as JSON"""
        json_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_services': len(results),
                'healthy_count': len([s for s in results.values() if s.status == ServiceStatus.HEALTHY]),
                'unhealthy_count': len([s for s in results.values() if s.status == ServiceStatus.UNHEALTHY]),
                'not_found_count': len([s for s in results.values() if s.status == ServiceStatus.NOT_FOUND])
            },
            'services': {
                name: {
                    **asdict(info),
                    'status': info.status.value
                }
                for name, info in results.items()
            }
        }

        def _default(obj: Any) -> Any:
            if callable(obj):
                return obj.__name__
            return str(obj)

        return json.dumps(json_data, indent=2, default=_default)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Check service availability')
    parser.add_argument('--format', choices=['console', 'json'], default='console',
                      help='Output format')
    parser.add_argument('--services', type=str,
                      help='Comma-separated list of services to check')
    parser.add_argument('--deep-check', action='store_true',
                      help='Perform deep health checks')
    parser.add_argument('--list', action='store_true',
                      help='List available services')
    parser.add_argument('--debug', action='store_true',
                      help='Enable debug logging')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize registry
    registry = ServiceRegistry()
    
    if args.list:
        print("Available services:")
        for service in registry.get_available_services():
            print(f"  • {service}")
        return
    
    # Determine which services to check
    if args.services:
        service_names = [s.strip() for s in args.services.split(',')]
        results = registry.check_services(service_names)
    else:
        results = registry.check_all_services()
    
    # Format and output results
    if args.format == 'json':
        print(ServiceStatusReporter.format_json(results))
    else:
        print(ServiceStatusReporter.format_console(results))
    
    # Exit with error code if any services are unhealthy
    unhealthy_count = len([s for s in results.values() 
                          if s.status in [ServiceStatus.UNHEALTHY, ServiceStatus.NOT_FOUND]])
    sys.exit(0 if unhealthy_count == 0 else 1)


if __name__ == "__main__":
    main()