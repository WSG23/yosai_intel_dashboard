#!/usr/bin/env python3
# minimal_dashboard.py
"""
Minimal Yōsai Intel Dashboard - Bypasses container issues for testing
This version manually creates services to avoid dependency injection deadlocks
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)

class MinimalYosaiDashboard:
    """Minimal dashboard that bypasses complex dependency injection"""
    
    def __init__(self):
        """Initialize minimal dashboard"""
        self.start_time = datetime.now()
        self.config_manager = None
        self._initialize_minimal_systems()
        
        print("🏯 Minimal Yōsai Intel Dashboard - Initialization Complete")
    
    def _initialize_minimal_systems(self):
        """Initialize systems without complex DI container"""
        try:
            print("📋 Loading configuration...")
            # 1. Load configuration directly
            from config.yaml_config import ConfigurationManager
            self.config_manager = ConfigurationManager()
            self.config_manager.load_configuration()
            print("✅ Configuration loaded")
            
            print("📊 Creating basic analytics...")
            # 2. Create basic analytics service directly
            from services.analytics_service import AnalyticsService
            self.analytics = AnalyticsService()
            print("✅ Analytics service created")
            
            print("🗄️  Setting up database...")
            # 3. Create database connection directly
            from config.database_manager import DatabaseManager
            self.database = DatabaseManager.create_connection()
            print("✅ Database connection established")
            
        except Exception as e:
            print(f"❌ Error during minimal initialization: {e}")
            raise
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get basic dashboard data"""
        try:
            # Simple dashboard data without complex dependencies
            return {
                'timestamp': datetime.now().isoformat(),
                'status': 'minimal_mode',
                'system_health': self.get_system_health(),
                'uptime_seconds': (datetime.now() - self.start_time).total_seconds()
            }
        except Exception as e:
            logging.error(f"Error getting dashboard data: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get basic system health"""
        try:
            health = {
                'overall': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'components': {}
            }
            
            # Test configuration
            if self.config_manager:
                health['components']['configuration'] = {
                    'status': 'healthy',
                    'source': getattr(self.config_manager, '_config_source', 'default')
                }
            
            # Test database
            if hasattr(self, 'database') and self.database:
                try:
                    # Simple database test
                    result = self.database.execute_query("SELECT 1 as test")
                    health['components']['database'] = {
                        'status': 'healthy' if not result.empty else 'warning',
                        'type': 'connected'
                    }
                except Exception as e:
                    health['components']['database'] = {
                        'status': 'error',
                        'error': str(e)
                    }
                    health['overall'] = 'degraded'
            
            # Test analytics
            if hasattr(self, 'analytics') and self.analytics:
                health['components']['analytics'] = {'status': 'healthy'}
            
            return health
            
        except Exception as e:
            return {
                'overall': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def test_core_functionality(self) -> Dict[str, Any]:
        """Test core functionality without complex operations"""
        results = {
            'configuration': False,
            'database': False,
            'analytics': False,
            'health_check': False
        }
        
        # Test configuration
        try:
            if self.config_manager:
                app_config = getattr(self.config_manager, 'app_config', None)
                results['configuration'] = app_config is not None
        except Exception as e:
            print(f"Configuration test failed: {e}")
        
        # Test database
        try:
            if hasattr(self, 'database'):
                test_result = self.database.execute_query("SELECT 1")
                results['database'] = not test_result.empty
        except Exception as e:
            print(f"Database test failed: {e}")
        
        # Test analytics
        try:
            if hasattr(self, 'analytics'):
                summary = self.analytics.get_dashboard_summary()
                results['analytics'] = summary is not None
        except Exception as e:
            print(f"Analytics test failed: {e}")
        
        # Test health check
        try:
            health = self.get_system_health()
            results['health_check'] = health.get('overall') in ['healthy', 'degraded']
        except Exception as e:
            print(f"Health check test failed: {e}")
        
        return results


def main():
    """Main entry point for minimal dashboard"""
    print("🏯 MINIMAL YŌSAI INTEL DASHBOARD")
    print("=" * 50)
    print("🧪 Testing basic functionality without complex DI")
    print("=" * 50)
    
    try:
        # Create minimal dashboard
        dashboard = MinimalYosaiDashboard()
        
        print("\n🔍 Running functionality tests...")
        test_results = dashboard.test_core_functionality()
        
        print(f"\n📊 Test Results:")
        for test_name, passed in test_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {test_name}: {status}")
        
        print(f"\n🏥 System Health Check...")
        health = dashboard.get_system_health()
        print(f"   Overall Status: {health.get('overall', 'unknown')}")
        
        print(f"\n📈 Dashboard Data...")
        data = dashboard.get_dashboard_data()
        print(f"   Status: {data.get('status', 'unknown')}")
        print(f"   Uptime: {data.get('uptime_seconds', 0):.1f} seconds")
        
        # Show configuration info
        if dashboard.config_manager:
            app_config = getattr(dashboard.config_manager, 'app_config', None)
            if app_config:
                print(f"\n🔧 Configuration Info:")
                print(f"   Host: {getattr(app_config, 'host', 'unknown')}")
                print(f"   Port: {getattr(app_config, 'port', 'unknown')}")
                print(f"   Debug: {getattr(app_config, 'debug', 'unknown')}")
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        if passed_tests == total_tests:
            print(f"\n🎉 ALL TESTS PASSED! ({passed_tests}/{total_tests})")
            print(f"✅ Basic Yōsai Intel Dashboard is working!")
            print(f"\n💡 Next steps:")
            print(f"   1. The core system works - container has dependency issues")
            print(f"   2. Fix the dependency injection circular references")
            print(f"   3. Check services registration order")
        else:
            print(f"\n⚠️  PARTIAL SUCCESS ({passed_tests}/{total_tests} tests passed)")
            print(f"🔧 Some components need attention")
        
        return dashboard
        
    except Exception as e:
        print(f"\n❌ Minimal dashboard failed: {e}")
        import traceback
        print("\n🔍 Error details:")
        traceback.print_exc()
        
        print(f"\n💡 Troubleshooting:")
        print(f"   1. Check if config/yaml_config.py exists")
        print(f"   2. Verify services/analytics_service.py exists")
        print(f"   3. Test database configuration")
        
        return None


if __name__ == "__main__":
    main()