#!/usr/bin/env python3
"""
YAML Configuration Migration & Backup System
============================================

Handles configuration migrations, backups, rollbacks, and version management.
Provides safe configuration updates with rollback capabilities.

Author: Assistant
Python Version: 3.8+
"""

import os
import json
import yaml
import shutil
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import tarfile
import tempfile


@dataclass
class ConfigurationVersion:
    """Represents a configuration version with metadata"""
    version_id: str
    timestamp: datetime
    files: Dict[str, str]  # filename -> file_hash
    description: str = ""
    author: str = ""
    tags: List[str] = field(default_factory=list)
    migration_applied: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'version_id': self.version_id,
            'timestamp': self.timestamp.isoformat(),
            'files': self.files,
            'description': self.description,
            'author': self.author,
            'tags': self.tags,
            'migration_applied': self.migration_applied
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConfigurationVersion':
        """Create from dictionary"""
        return cls(
            version_id=data['version_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            files=data['files'],
            description=data.get('description', ''),
            author=data.get('author', ''),
            tags=data.get('tags', []),
            migration_applied=data.get('migration_applied', False)
        )


class ConfigurationMigration(ABC):
    """Base class for configuration migrations"""
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Migration version identifier"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Migration description"""
        pass
    
    @abstractmethod
    def apply(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply migration to configuration data"""
        pass
    
    @abstractmethod
    def rollback(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Rollback migration from configuration data"""
        pass
    
    def validate(self, config_data: Dict[str, Any]) -> List[str]:
        """Validate configuration before applying migration"""
        return []


class AddMonitoringSection(ConfigurationMigration):
    """Migration to add monitoring section to configurations"""
    
    @property
    def version(self) -> str:
        return "001_add_monitoring"
    
    @property
    def description(self) -> str:
        return "Add monitoring section with health checks and metrics"
    
    def apply(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add monitoring section if missing"""
        if 'monitoring' not in config_data:
            config_data['monitoring'] = {
                'health_check_enabled': True,
                'metrics_enabled': True,
                'health_check_interval_seconds': 30,
                'performance_monitoring': False,
                'error_reporting_enabled': False
            }
        return config_data
    
    def rollback(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove monitoring section"""
        if 'monitoring' in config_data:
            del config_data['monitoring']
        return config_data


class UpdateSecurityDefaults(ConfigurationMigration):
    """Migration to update security defaults"""
    
    @property
    def version(self) -> str:
        return "002_update_security"
    
    @property
    def description(self) -> str:
        return "Update security section with enhanced defaults"
    
    def apply(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update security configuration"""
        if 'security' in config_data:
            security = config_data['security']
            
            # Add missing security fields
            if 'rate_limiting_enabled' not in security:
                security['rate_limiting_enabled'] = True
            
            if 'rate_limit_per_minute' not in security:
                security['rate_limit_per_minute'] = 120
            
            if 'allowed_file_types' not in security:
                security['allowed_file_types'] = ['.csv', '.json', '.xlsx', '.xls']
            
            # Update session timeout if it's too long
            if security.get('session_timeout_minutes', 0) > 240:
                security['session_timeout_minutes'] = 60
        
        return config_data
    
    def rollback(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Rollback security updates"""
        if 'security' in config_data:
            security = config_data['security']
            
            # Remove added fields
            fields_to_remove = ['rate_limiting_enabled', 'rate_limit_per_minute', 'allowed_file_types']
            for field in fields_to_remove:
                if field in security:
                    del security[field]
        
        return config_data


class MigrateAnalyticsConfig(ConfigurationMigration):
    """Migration to update analytics configuration structure"""
    
    @property
    def version(self) -> str:
        return "003_migrate_analytics"
    
    @property
    def description(self) -> str:
        return "Migrate analytics configuration to new structure"
    
    def apply(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate analytics configuration"""
        if 'analytics' in config_data:
            analytics = config_data['analytics']
            
            # Rename old fields
            if 'timeout_seconds' in analytics:
                analytics['cache_timeout_seconds'] = analytics.pop('timeout_seconds')
            
            if 'max_records' in analytics:
                analytics['max_records_per_query'] = analytics.pop('max_records')
            
            # Add new fields
            if 'anomaly_detection_enabled' not in analytics:
                analytics['anomaly_detection_enabled'] = True
            
            if 'data_retention_days' not in analytics:
                analytics['data_retention_days'] = 365
        
        return config_data
    
    def rollback(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Rollback analytics migration"""
        if 'analytics' in config_data:
            analytics = config_data['analytics']
            
            # Restore old field names
            if 'cache_timeout_seconds' in analytics:
                analytics['timeout_seconds'] = analytics.pop('cache_timeout_seconds')
            
            if 'max_records_per_query' in analytics:
                analytics['max_records'] = analytics.pop('max_records_per_query')
            
            # Remove new fields
            new_fields = ['anomaly_detection_enabled', 'data_retention_days']
            for field in new_fields:
                if field in analytics:
                    del analytics[field]
        
        return config_data


class ConfigurationBackupManager:
    """Manages configuration backups and versions"""
    
    def __init__(self, backup_dir: str = "config_backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.versions_file = self.backup_dir / "versions.json"
        self.logger = logging.getLogger(__name__)
        
        # Load existing versions
        self.versions = self._load_versions()
    
    def _load_versions(self) -> List[ConfigurationVersion]:
        """Load version history from file"""
        if self.versions_file.exists():
            try:
                with open(self.versions_file, 'r') as f:
                    data = json.load(f)
                return [ConfigurationVersion.from_dict(v) for v in data]
            except Exception as e:
                self.logger.error(f"Failed to load versions: {e}")
        
        return []
    
    def _save_versions(self) -> None:
        """Save version history to file"""
        try:
            with open(self.versions_file, 'w') as f:
                json.dump([v.to_dict() for v in self.versions], f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save versions: {e}")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def create_backup(self, config_dir: str, description: str = "", 
                     author: str = "", tags: List[str] = None) -> str:
        """Create a backup of configuration directory"""
        config_path = Path(config_dir)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration directory not found: {config_dir}")
        
        # Generate version ID
        timestamp = datetime.now()
        version_id = f"v{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        # Create backup directory
        backup_path = self.backup_dir / version_id
        backup_path.mkdir(exist_ok=True)
        
        # Copy configuration files and calculate hashes
        file_hashes = {}
        config_files = list(config_path.glob("*.yaml")) + list(config_path.glob("*.yml"))
        
        for config_file in config_files:
            dest_file = backup_path / config_file.name
            shutil.copy2(config_file, dest_file)
            file_hashes[config_file.name] = self._calculate_file_hash(str(dest_file))
        
        # Create version record
        version = ConfigurationVersion(
            version_id=version_id,
            timestamp=timestamp,
            files=file_hashes,
            description=description,
            author=author,
            tags=tags or []
        )
        
        self.versions.append(version)
        self._save_versions()
        
        self.logger.info(f"Created backup {version_id} with {len(file_hashes)} files")
        return version_id
    
    def restore_backup(self, version_id: str, target_dir: str) -> bool:
        """Restore configuration from backup"""
        version = self.get_version(version_id)
        if not version:
            raise ValueError(f"Version {version_id} not found")
        
        backup_path = self.backup_dir / version_id
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup directory not found: {backup_path}")
        
        target_path = Path(target_dir)
        target_path.mkdir(exist_ok=True)
        
        # Restore files
        restored_files = []
        for filename in version.files:
            source_file = backup_path / filename
            dest_file = target_path / filename
            
            if source_file.exists():
                shutil.copy2(source_file, dest_file)
                restored_files.append(filename)
            else:
                self.logger.warning(f"Backup file not found: {source_file}")
        
        self.logger.info(f"Restored {len(restored_files)} files from {version_id}")
        return len(restored_files) == len(version.files)
    
    def get_version(self, version_id: str) -> Optional[ConfigurationVersion]:
        """Get version by ID"""
        for version in self.versions:
            if version.version_id == version_id:
                return version
        return None
    
    def list_versions(self, limit: int = 10) -> List[ConfigurationVersion]:
        """List recent versions"""
        return sorted(self.versions, key=lambda v: v.timestamp, reverse=True)[:limit]
    
    def cleanup_old_backups(self, keep_days: int = 30, keep_count: int = 10) -> int:
        """Clean up old backups"""
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        # Sort versions by timestamp
        sorted_versions = sorted(self.versions, key=lambda v: v.timestamp, reverse=True)
        
        # Keep recent versions and versions within date range
        versions_to_keep = []
        versions_to_remove = []
        
        for i, version in enumerate(sorted_versions):
            if i < keep_count or version.timestamp > cutoff_date:
                versions_to_keep.append(version)
            else:
                versions_to_remove.append(version)
        
        # Remove old backup directories
        removed_count = 0
        for version in versions_to_remove:
            backup_path = self.backup_dir / version.version_id
            if backup_path.exists():
                shutil.rmtree(backup_path)
                removed_count += 1
        
        # Update versions list
        self.versions = versions_to_keep
        self._save_versions()
        
        self.logger.info(f"Cleaned up {removed_count} old backups")
        return removed_count
    
    def create_archive(self, version_id: str, archive_path: str) -> bool:
        """Create compressed archive of backup"""
        version = self.get_version(version_id)
        if not version:
            raise ValueError(f"Version {version_id} not found")
        
        backup_path = self.backup_dir / version_id
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup directory not found: {backup_path}")
        
        try:
            with tarfile.open(archive_path, 'w:gz') as tar:
                tar.add(backup_path, arcname=version_id)
            
            self.logger.info(f"Created archive {archive_path} for {version_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to create archive: {e}")
            return False


class ConfigurationMigrationManager:
    """Manages configuration migrations"""
    
    def __init__(self, backup_manager: ConfigurationBackupManager):
        self.backup_manager = backup_manager
        self.logger = logging.getLogger(__name__)
        
        # Register available migrations
        self.migrations = [
            AddMonitoringSection(),
            UpdateSecurityDefaults(),
            MigrateAnalyticsConfig()
        ]
    
    def get_pending_migrations(self, config_dir: str) -> List[ConfigurationMigration]:
        """Get migrations that haven't been applied"""
        # For this example, we'll check if migration markers exist
        config_path = Path(config_dir)
        migration_file = config_path / ".migrations"
        
        applied_migrations = set()
        if migration_file.exists():
            try:
                with open(migration_file, 'r') as f:
                    applied_migrations = set(f.read().strip().split('\n'))
            except Exception:
                pass
        
        return [m for m in self.migrations if m.version not in applied_migrations]
    
    def apply_migration(self, migration: ConfigurationMigration, 
                       config_dir: str, dry_run: bool = False) -> Dict[str, Any]:
        """Apply a single migration"""
        config_path = Path(config_dir)
        results = {
            'migration': migration.version,
            'description': migration.description,
            'files_processed': [],
            'errors': [],
            'dry_run': dry_run
        }
        
        # Create backup before applying migration
        if not dry_run:
            backup_id = self.backup_manager.create_backup(
                config_dir,
                f"Pre-migration backup for {migration.version}",
                tags=['migration', migration.version]
            )
            results['backup_id'] = backup_id
        
        # Process each YAML file
        config_files = list(config_path.glob("*.yaml")) + list(config_path.glob("*.yml"))
        
        for config_file in config_files:
            try:
                # Load configuration
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}
                
                # Validate before migration
                validation_errors = migration.validate(config_data)
                if validation_errors:
                    results['errors'].extend([f"{config_file.name}: {err}" for err in validation_errors])
                    continue
                
                # Apply migration
                migrated_data = migration.apply(config_data.copy())
                
                # Save migrated configuration
                if not dry_run:
                    with open(config_file, 'w', encoding='utf-8') as f:
                        yaml.dump(migrated_data, f, default_flow_style=False, 
                                allow_unicode=True, sort_keys=False)
                
                results['files_processed'].append(config_file.name)
                
            except Exception as e:
                error_msg = f"{config_file.name}: {str(e)}"
                results['errors'].append(error_msg)
                self.logger.error(f"Migration {migration.version} failed for {config_file}: {e}")
        
        # Mark migration as applied
        if not dry_run and not results['errors']:
            self._mark_migration_applied(config_dir, migration.version)
        
        return results
    
    def rollback_migration(self, migration_version: str, config_dir: str) -> Dict[str, Any]:
        """Rollback a specific migration"""
        # Find migration
        migration = None
        for m in self.migrations:
            if m.version == migration_version:
                migration = m
                break
        
        if not migration:
            raise ValueError(f"Migration {migration_version} not found")
        
        config_path = Path(config_dir)
        results = {
            'migration': migration_version,
            'files_processed': [],
            'errors': []
        }
        
        # Create backup before rollback
        backup_id = self.backup_manager.create_backup(
            config_dir,
            f"Pre-rollback backup for {migration_version}",
            tags=['rollback', migration_version]
        )
        results['backup_id'] = backup_id
        
        # Process each YAML file
        config_files = list(config_path.glob("*.yaml")) + list(config_path.glob("*.yml"))
        
        for config_file in config_files:
            try:
                # Load configuration
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}
                
                # Rollback migration
                rolled_back_data = migration.rollback(config_data.copy())
                
                # Save rolled back configuration
                with open(config_file, 'w', encoding='utf-8') as f:
                    yaml.dump(rolled_back_data, f, default_flow_style=False, 
                            allow_unicode=True, sort_keys=False)
                
                results['files_processed'].append(config_file.name)
                
            except Exception as e:
                error_msg = f"{config_file.name}: {str(e)}"
                results['errors'].append(error_msg)
                self.logger.error(f"Rollback {migration_version} failed for {config_file}: {e}")
        
        # Remove migration marker
        if not results['errors']:
            self._unmark_migration_applied(config_dir, migration_version)
        
        return results
    
    def apply_all_pending(self, config_dir: str, dry_run: bool = False) -> List[Dict[str, Any]]:
        """Apply all pending migrations"""
        pending = self.get_pending_migrations(config_dir)
        results = []
        
        for migration in pending:
            result = self.apply_migration(migration, config_dir, dry_run)
            results.append(result)
            
            # Stop if there were errors
            if result['errors']:
                self.logger.error(f"Migration {migration.version} failed, stopping")
                break
        
        return results
    
    def _mark_migration_applied(self, config_dir: str, migration_version: str) -> None:
        """Mark migration as applied"""
        config_path = Path(config_dir)
        migration_file = config_path / ".migrations"
        
        applied_migrations = set()
        if migration_file.exists():
            try:
                with open(migration_file, 'r') as f:
                    applied_migrations = set(f.read().strip().split('\n'))
            except Exception:
                pass
        
        applied_migrations.add(migration_version)
        
        with open(migration_file, 'w') as f:
            f.write('\n'.join(sorted(applied_migrations)))
    
    def _unmark_migration_applied(self, config_dir: str, migration_version: str) -> None:
        """Remove migration marker"""
        config_path = Path(config_dir)
        migration_file = config_path / ".migrations"
        
        if migration_file.exists():
            try:
                with open(migration_file, 'r') as f:
                    applied_migrations = set(f.read().strip().split('\n'))
                
                applied_migrations.discard(migration_version)
                
                with open(migration_file, 'w') as f:
                    f.write('\n'.join(sorted(applied_migrations)))
            except Exception as e:
                self.logger.error(f"Failed to unmark migration: {e}")


class ConfigurationMonitor:
    """Monitors configuration changes and triggers actions"""
    
    def __init__(self, config_dir: str, backup_manager: ConfigurationBackupManager):
        self.config_dir = Path(config_dir)
        self.backup_manager = backup_manager
        self.logger = logging.getLogger(__name__)
        
        # Track file modification times
        self.last_modified = {}
        self._update_modification_times()
    
    def _update_modification_times(self) -> None:
        """Update file modification time tracking"""
        config_files = list(self.config_dir.glob("*.yaml")) + list(self.config_dir.glob("*.yml"))
        
        for config_file in config_files:
            if config_file.exists():
                self.last_modified[config_file.name] = config_file.stat().st_mtime
    
    def check_for_changes(self) -> List[str]:
        """Check for configuration file changes"""
        changed_files = []
        config_files = list(self.config_dir.glob("*.yaml")) + list(self.config_dir.glob("*.yml"))
        
        for config_file in config_files:
            if config_file.exists():
                current_mtime = config_file.stat().st_mtime
                last_mtime = self.last_modified.get(config_file.name, 0)
                
                if current_mtime > last_mtime:
                    changed_files.append(config_file.name)
                    self.last_modified[config_file.name] = current_mtime
        
        return changed_files
    
    def auto_backup_on_change(self, check_interval: int = 60) -> None:
        """Automatically create backups when changes are detected"""
        import time
        
        self.logger.info(f"Starting configuration monitor (checking every {check_interval}s)")
        
        try:
            while True:
                changed_files = self.check_for_changes()
                
                if changed_files:
                    self.logger.info(f"Configuration changes detected: {changed_files}")
                    
                    try:
                        backup_id = self.backup_manager.create_backup(
                            str(self.config_dir),
                            f"Auto-backup due to changes in: {', '.join(changed_files)}",
                            tags=['auto-backup']
                        )
                        self.logger.info(f"Created auto-backup: {backup_id}")
                    except Exception as e:
                        self.logger.error(f"Failed to create auto-backup: {e}")
                
                time.sleep(check_interval)
        
        except KeyboardInterrupt:
            self.logger.info("Configuration monitor stopped")


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Configuration Migration & Backup System")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Backup commands
    backup_parser = subparsers.add_parser('backup', help='Create configuration backup')
    backup_parser.add_argument('config_dir', help='Configuration directory')
    backup_parser.add_argument('--description', '-d', default='', help='Backup description')
    backup_parser.add_argument('--author', '-a', default='', help='Backup author')
    backup_parser.add_argument('--tag', '-t', action='append', help='Backup tags')
    
    # Restore commands
    restore_parser = subparsers.add_parser('restore', help='Restore configuration backup')
    restore_parser.add_argument('version_id', help='Version ID to restore')
    restore_parser.add_argument('target_dir', help='Target directory')
    
    # List versions
    list_parser = subparsers.add_parser('list', help='List backup versions')
    list_parser.add_argument('--limit', '-l', type=int, default=10, help='Limit results')
    
    # Migration commands
    migrate_parser = subparsers.add_parser('migrate', help='Apply migrations')
    migrate_parser.add_argument('config_dir', help='Configuration directory')
    migrate_parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    migrate_parser.add_argument('--migration', '-m', help='Apply specific migration')
    
    # Rollback commands
    rollback_parser = subparsers.add_parser('rollback', help='Rollback migration')
    rollback_parser.add_argument('config_dir', help='Configuration directory')
    rollback_parser.add_argument('migration_version', help='Migration version to rollback')
    
    # Monitor commands
    monitor_parser = subparsers.add_parser('monitor', help='Monitor configuration changes')
    monitor_parser.add_argument('config_dir', help='Configuration directory')
    monitor_parser.add_argument('--interval', '-i', type=int, default=60, 
                               help='Check interval in seconds')
    
    # Cleanup commands
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old backups')
    cleanup_parser.add_argument('--days', type=int, default=30, help='Keep backups newer than N days')
    cleanup_parser.add_argument('--count', type=int, default=10, help='Keep N most recent backups')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        backup_manager = ConfigurationBackupManager()
        
        if args.command == 'backup':
            version_id = backup_manager.create_backup(
                args.config_dir,
                args.description,
                args.author,
                args.tag or []
            )
            print(f"✅ Created backup: {version_id}")
        
        elif args.command == 'restore':
            success = backup_manager.restore_backup(args.version_id, args.target_dir)
            if success:
                print(f"✅ Restored backup {args.version_id} to {args.target_dir}")
            else:
                print(f"❌ Failed to restore backup {args.version_id}")
                return 1
        
        elif args.command == 'list':
            versions = backup_manager.list_versions(args.limit)
            if versions:
                print("Configuration Backup Versions:")
                print("-" * 50)
                for version in versions:
                    tags_str = f" [{', '.join(version.tags)}]" if version.tags else ""
                    print(f"{version.version_id} - {version.timestamp.strftime('%Y-%m-%d %H:%M:%S')}{tags_str}")
                    if version.description:
                        print(f"  Description: {version.description}")
                    print(f"  Files: {len(version.files)}")
                    print()
            else:
                print("No backup versions found")
        
        elif args.command == 'migrate':
            migration_manager = ConfigurationMigrationManager(backup_manager)
            
            if args.migration:
                # Apply specific migration
                migration = None
                for m in migration_manager.migrations:
                    if m.version == args.migration:
                        migration = m
                        break
                
                if not migration:
                    print(f"❌ Migration {args.migration} not found")
                    return 1
                
                result = migration_manager.apply_migration(migration, args.config_dir, args.dry_run)
                
                if result['errors']:
                    print(f"❌ Migration {args.migration} failed:")
                    for error in result['errors']:
                        print(f"  - {error}")
                    return 1
                else:
                    action = "Would apply" if args.dry_run else "Applied"
                    print(f"✅ {action} migration {args.migration}")
                    print(f"  Files processed: {len(result['files_processed'])}")
            else:
                # Apply all pending migrations
                results = migration_manager.apply_all_pending(args.config_dir, args.dry_run)
                
                total_errors = sum(len(r['errors']) for r in results)
                if total_errors > 0:
                    print(f"❌ {total_errors} migration errors occurred")
                    return 1
                else:
                    action = "Would apply" if args.dry_run else "Applied"
                    print(f"✅ {action} {len(results)} migrations")
        
        elif args.command == 'rollback':
            migration_manager = ConfigurationMigrationManager(backup_manager)
            result = migration_manager.rollback_migration(args.migration_version, args.config_dir)
            
            if result['errors']:
                print(f"❌ Rollback {args.migration_version} failed:")
                for error in result['errors']:
                    print(f"  - {error}")
                return 1
            else:
                print(f"✅ Rolled back migration {args.migration_version}")
                print(f"  Files processed: {len(result['files_processed'])}")
        
        elif args.command == 'monitor':
            monitor = ConfigurationMonitor(args.config_dir, backup_manager)
            monitor.auto_backup_on_change(args.interval)
        
        elif args.command == 'cleanup':
            removed_count = backup_manager.cleanup_old_backups(args.days, args.count)
            print(f"✅ Cleaned up {removed_count} old backups")
        
        return 0
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())