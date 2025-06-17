#!/usr/bin/env python3
"""
Service Availability Checker - Modular Design
==============================================

A comprehensive, modular service checker that integrates with your existing
DI container system and follows your project's architectural patterns.

Usage:
    python3 check_services.py
    python3 check_services.py --format json
    python3 check_services.py --services analytics,database
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
import importlib.util
import logging

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
            # Try to import your existing DI container
            from core.di_container import Container, get_configured_container
            
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
        from core.di_container import get_configured_container
        
        container = get_configured_container()
        health = container.health_check()
        
        return {
            'container_name': health.get('container', 'unknown'),
            'total_services': len(health.get('services', {})),
            'healthy_services': len([
                s for s in health.get('services', {}).values() 
                if s.get('status') == 'healthy'
            ]),
            'dependency_graph_size': len(health.get('dependency_graph', {})),
            'startup_order_length': len(health.get('startup_order', []))
        }


class DatabaseChecker(ServiceChecker):
    """Checks database connectivity"""
    
    def __init__(self):
        super().__init__("database")
    
    def check(self) -> ServiceInfo:
        try:
            from config.database_manager import DatabaseManager
            
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
        from config.database_manager import DatabaseManager
        
        db_manager = DatabaseManager()
        
        # Try to get a connection
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            return {
                'connection_successful': True,
                'test_query_result': result[0] if result else None,
                'database_type': db_manager.db_config.db_type
            }


class AnalyticsServiceChecker(ServiceChecker):
    """Checks analytics service"""
    
    def __init__(self):
        super().__init__("analytics_service")
    
    def check(self) -> ServiceInfo:
        try:
            from services.analytics_service import AnalyticsService
            
            result, response_time = self._measure_response_time(
                lambda: self._check_analytics_health()
            )
            
            return ServiceInfo(
                name="analytics_service",
                status=ServiceStatus.HEALTHY,
                type="business_logic",
                layer="service",
                dependencies=["database"],
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
        from services.analytics_service import AnalyticsService
        from core.di_container import get_configured_container
        
        container = get_configured_container()
        analytics = container.get('analytics_service')
        
        # Test basic functionality
        try:
            summary = analytics.get_dashboard_summary()
            return {
                'dashboard_summary_available': True,
                'last_updated': summary.get('last_updated'),
                'system_status': summary.get('system_status'),
                'has_recent_data': summary.get('recent_events_24h', 0) > 0
            }
        except Exception as e:
            return {
                'dashboard_summary_available': False,
                'error': str(e)
            }


class ConfigurationChecker(ServiceChecker):
    """Checks configuration system"""
    
    def __init__(self):
        super().__init__("configuration")
    
    def check(self) -> ServiceInfo:
        try:
            from config.configuration_manager import ConfigurationManager
            
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
        from config.configuration_manager import ConfigurationManager
        
        config_manager = ConfigurationManager()
        config_manager.load_configuration()
        
        return {
            'config_loaded': config_manager._config_source is not None,
            'environment': config_manager.environment,
            'config_file_path': getattr(config_manager, 'config_file_path', 'unknown')
        }


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
        
        return self.checkers[name].check()
    
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
        
        # Summary
        total = len(results)
        healthy = len([s for s in results.values() if s.status == ServiceStatus.HEALTHY])
        output.append(f"\n📈 SUMMARY: {healthy}/{total} services healthy")
        
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
            'services': {name: asdict(info) for name, info in results.items()}
        }
        return json.dumps(json_data, indent=2)


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
    
    args = parser.parse_args()
    
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