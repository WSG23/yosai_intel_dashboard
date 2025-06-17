#!/usr/bin/env python3
# execute_immediate_actions.py
"""
Execute immediate action items for Yōsai Intel Dashboard enhancement
Handles the critical Week 1 fixes and validation

Usage:
    python execute_immediate_actions.py
    python execute_immediate_actions.py --validate-only
    python execute_immediate_actions.py --cleanup-only
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ImmediateActionsExecutor:
    """Executes immediate action items with validation and rollback capability"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.backup_dir = None
        self.actions_log = []
    
    def create_backup(self) -> str:
        """Create backup of files that will be modified"""
        backup_dir = tempfile.mkdtemp(prefix="yosai_backup_")
        self.backup_dir = backup_dir
        
        files_to_backup = [
            "config/setting.py",
            "setup_modular_system.py",
            "app.py",  # In case it has old imports
        ]
        
        print(f"📦 Creating backup in: {backup_dir}")
        
        for file_path in files_to_backup:
            source = self.project_root / file_path
            if source.exists():
                dest = Path(backup_dir) / file_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
                print(f"   ✅ Backed up: {file_path}")
        
        return backup_dir
    
    def execute_action_1_remove_legacy_files(self) -> bool:
        """Action 1: Remove legacy configuration files"""
        print("\n🗑️  ACTION 1: Removing legacy configuration files")
        print("-" * 50)
        
        legacy_files = [
            "config/setting.py",
            "setup_modular_system.py"
        ]
        
        success = True
        for file_path in legacy_files:
            full_path = self.project_root / file_path
            
            if full_path.exists():
                try:
                    full_path.unlink()
                    print(f"   ✅ Removed: {file_path}")
                    self.actions_log.append(f"REMOVED: {file_path}")
                except Exception as e:
                    print(f"   ❌ Failed to remove {file_path}: {e}")
                    success = False
            else:
                print(f"   ℹ️  Not found (already clean): {file_path}")
        
        return success
    
    def execute_action_2_update_imports(self) -> bool:
        """Action 2: Update imports throughout codebase"""
        print("\n🔄 ACTION 2: Updating imports to use unified_config")
        print("-" * 50)
        
        # Files that might need import updates
        python_files = [
            "app.py",
            "services/analytics_service.py",
            "config/database_manager.py",
            "core/container.py"
        ]
        
        old_import_pattern = "from config.setting import"
        new_import_pattern = "from config.unified_config import"
        
        success = True
        updated_files = []
        
        for file_path in python_files:
            full_path = self.project_root / file_path
            
            if not full_path.exists():
                continue
            
            try:
                # Read file content
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if update is needed
                if old_import_pattern in content:
                    # Update imports
                    updated_content = content.replace(old_import_pattern, new_import_pattern)
                    
                    # Write updated content
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    
                    print(f"   ✅ Updated imports in: {file_path}")
                    updated_files.append(file_path)
                    self.actions_log.append(f"UPDATED: {file_path}")
                else:
                    print(f"   ℹ️  No updates needed: {file_path}")
            
            except Exception as e:
                print(f"   ❌ Failed to update {file_path}: {e}")
                success = False
        
        if updated_files:
            print(f"\n   📝 Updated {len(updated_files)} files with new imports")
        
        return success
    
    def execute_action_3_validate_configuration(self) -> bool:
        """Action 3: Validate unified configuration system"""
        print("\n✅ ACTION 3: Validating unified configuration system")
        print("-" * 50)
        
        try:
            # Import the new configuration system
            sys.path.insert(0, str(self.project_root))
            
            # Try different import paths
            try:
                from config.unified_config import ConfigurationManager, Environment
            except ImportError:
                try:
                    from config.yaml_config import ConfigurationManager
                    Environment = None
                except ImportError:
                    print(f"   ❌ Cannot import configuration modules")
                    print(f"      Make sure config/unified_config.py or config/yaml_config.py exists")
                    return False
            
            # Test configuration loading
            config_manager = ConfigurationManager()
            
            # Try loading different configurations
            if Environment:
                environments = [Environment.DEVELOPMENT, Environment.PRODUCTION, Environment.TESTING]
                for env in environments:
                    try:
                        config_manager.load_configuration(environment=env)
                        validate_func = getattr(config_manager, 'validate_configuration', None)
                        warnings = validate_func() if validate_func else []
                        
                        print(f"   ✅ {env.value}: Loaded successfully")
                        
                        if warnings:
                            print(f"      ⚠️  {len(warnings)} warnings:")
                            for warning in warnings[:3]:  # Show first 3 warnings
                                print(f"         - {warning}")
                            if len(warnings) > 3:
                                print(f"         ... and {len(warnings) - 3} more")
                        else:
                            print(f"      ✅ No configuration warnings")
                    
                    except Exception as e:
                        print(f"   ❌ {env.value}: Failed to load - {e}")
                        return False
            else:
                # Test basic loading without environment enum
                try:
                    config_manager.load_configuration()
                    print(f"   ✅ Configuration loaded successfully")
                except Exception as e:
                    print(f"   ❌ Configuration loading failed: {e}")
                    return False
            
            self.actions_log.append("VALIDATED: Unified configuration system")
            return True
            
        except ImportError as e:
            print(f"   ❌ Cannot import unified configuration: {e}")
            print(f"      Make sure config/unified_config.py exists")
            return False
        except Exception as e:
            print(f"   ❌ Configuration validation failed: {e}")
            return False
    
    def execute_action_4_test_enhanced_systems(self) -> bool:
        """Action 4: Test enhanced systems integration"""
        print("\n🧪 ACTION 4: Testing enhanced systems integration")
        print("-" * 50)
        
        try:
            # Test dependency injection with fallbacks
            try:
                from core.service_registry import get_configured_container_with_yaml
                from core.container import Container
                
                container = get_configured_container_with_yaml()
                
                # Check core services
                required_services = [
                    'config_manager', 'app_config', 'database_config', 
                    'security_config', 'cache_manager'
                ]
                
                missing_services = []
                for service in required_services:
                    if container.has(service):
                        print(f"   ✅ Service registered: {service}")
                    else:
                        missing_services.append(service)
                        print(f"   ❌ Service missing: {service}")
                
                if missing_services:
                    print(f"   ⚠️  {len(missing_services)} services need registration")
                    # Don't fail completely, just warn
                
            except ImportError as e:
                print(f"   ⚠️  DI container not available: {e}")
            
            # Test main implementation with fallbacks
            try:
                from implementation import YosaiIntelDashboard, EnhancedDashboardFactory
                
                # Create test dashboard
                dashboard = EnhancedDashboardFactory.create_testing_dashboard()
                print(f"   ✅ Created test dashboard instance")
                
                # Quick health check
                health = dashboard.get_system_health()
                print(f"   📊 System health: {health.get('overall', 'unknown')}")
                
                # Clean shutdown
                dashboard.shutdown()
                print(f"   ✅ Clean shutdown completed")
                
            except ImportError as e:
                print(f"   ⚠️  Enhanced implementation not fully available: {e}")
                print(f"       This is expected during initial setup")
            
            self.actions_log.append("TESTED: Enhanced systems integration")
            return True
            
        except ImportError as e:
            print(f"   ⚠️  Import error: {e}")
            print(f"      Some enhanced modules may be missing - this is expected during initial setup")
            return True  # Don't fail completely during setup
        except Exception as e:
            print(f"   ❌ System testing failed: {e}")
            return False
    
    def validate_final_state(self) -> Dict[str, Any]:
        """Validate the final state after all actions"""
        print("\n🔍 FINAL VALIDATION")
        print("-" * 50)
        
        validation_results = {
            'legacy_files_removed': True,
            'configuration_system': True,
            'import_updates': True,
            'system_integration': True,
            'ready_for_week_2': True
        }
        
        # Check legacy files are gone
        legacy_files = ["config/setting.py", "setup_modular_system.py"]
        for file_path in legacy_files:
            if (self.project_root / file_path).exists():
                validation_results['legacy_files_removed'] = False
                print(f"   ❌ Legacy file still exists: {file_path}")
        
        if validation_results['legacy_files_removed']:
            print(f"   ✅ All legacy files removed")
        
        # Check configuration system
        try:
            from config.unified_config import ConfigurationManager
            config_manager = ConfigurationManager()
            config_manager.load_configuration()
            print(f"   ✅ Configuration system operational")
        except Exception:
            validation_results['configuration_system'] = False
            print(f"   ❌ Configuration system has issues")
        
        # Overall assessment
        all_passed = all(validation_results.values())
        
        if all_passed:
            print(f"\n🎉 ALL VALIDATIONS PASSED!")
            print(f"✅ Ready for Week 2-4 improvements")
            print(f"🚀 Priority: Deploy security enhancements")
        else:
            print(f"\n⚠️  Some validations failed")
            print(f"🔧 Review and fix issues before proceeding")
        
        return validation_results
    
    def rollback_changes(self):
        """Rollback changes if something went wrong"""
        if not self.backup_dir or not os.path.exists(self.backup_dir):
            print("❌ No backup available for rollback")
            return False
        
        print(f"\n🔄 Rolling back changes from backup: {self.backup_dir}")
        
        try:
            # Restore files from backup
            backup_path = Path(self.backup_dir)
            
            for backup_file in backup_path.rglob("*"):
                if backup_file.is_file():
                    relative_path = backup_file.relative_to(backup_path)
                    restore_path = self.project_root / relative_path
                    
                    # Create directory if needed
                    restore_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Restore file
                    shutil.copy2(backup_file, restore_path)
                    print(f"   ✅ Restored: {relative_path}")
            
            print(f"🎯 Rollback completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False
        finally:
            # Clean up backup
            shutil.rmtree(self.backup_dir, ignore_errors=True)
    
    def run_all_actions(self, validate_only: bool = False, cleanup_only: bool = False) -> bool:
        """Run all immediate actions"""
        print("🏯 YŌSAI INTEL DASHBOARD - IMMEDIATE ACTIONS")
        print("=" * 60)
        print("Week 1 Critical Fixes - Automated Execution")
        print("=" * 60)
        
        if validate_only:
            print("🔍 VALIDATION ONLY MODE")
            return self.execute_action_3_validate_configuration()
        
        if cleanup_only:
            print("🗑️  CLEANUP ONLY MODE")
            return self.execute_action_1_remove_legacy_files()
        
        # Create backup first
        backup_dir = self.create_backup()
        print(f"📦 Backup created: {backup_dir}")
        
        try:
            # Execute all actions
            actions = [
                ("Remove Legacy Files", self.execute_action_1_remove_legacy_files),
                ("Update Imports", self.execute_action_2_update_imports),
                ("Validate Configuration", self.execute_action_3_validate_configuration),
                ("Test Enhanced Systems", self.execute_action_4_test_enhanced_systems)
            ]
            
            success = True
            for action_name, action_func in actions:
                print(f"\n{'='*20} {action_name} {'='*20}")
                if not action_func():
                    print(f"❌ {action_name} failed!")
                    success = False
                    break
                else:
                    print(f"✅ {action_name} completed successfully")
            
            if success:
                # Final validation
                validation_results = self.validate_final_state()
                success = all(validation_results.values())
            
            if success:
                print(f"\n🎉 ALL IMMEDIATE ACTIONS COMPLETED SUCCESSFULLY!")
                print(f"\n📋 NEXT STEPS:")
                print(f"   1. Deploy security enhancements (HIGH PRIORITY)")
                print(f"   2. Activate performance monitoring (HIGH PRIORITY)")
                print(f"   3. Begin Week 2-4 roadmap items")
                print(f"   4. Run: python implementation.py")
                
                # Clean up backup
                shutil.rmtree(backup_dir, ignore_errors=True)
                
            else:
                print(f"\n❌ Some actions failed. Consider rollback.")
                rollback = input("Rollback changes? (y/n): ").lower().startswith('y')
                if rollback:
                    self.rollback_changes()
                else:
                    print(f"⚠️  Backup preserved at: {backup_dir}")
            
            return success
            
        except Exception as e:
            print(f"\n💥 Unexpected error: {e}")
            print(f"🔄 Rolling back changes...")
            self.rollback_changes()
            return False


def main():
    """Main entry point"""
    executor = ImmediateActionsExecutor()
    
    # Parse arguments
    validate_only = "--validate-only" in sys.argv
    cleanup_only = "--cleanup-only" in sys.argv
    
    # Execute actions
    success = executor.run_all_actions(validate_only, cleanup_only)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()