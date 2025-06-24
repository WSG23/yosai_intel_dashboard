from typing import Dict, Any, List
from pathlib import Path

class ConfigurationValidator:
    """Isolated configuration validation"""

    def __init__(self):
        self.required_sections = ['database', 'app', 'logging']
        self.section_schemas = {
            'database': ['host', 'port', 'name'],
            'app': ['debug', 'secret_key'],
            'logging': ['level', 'format']
        }

    def validate(self, config: Dict[str, Any]) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []

        for section in self.required_sections:
            if section not in config:
                errors.append(f"Missing required section: {section}")
                continue

            if section in self.section_schemas:
                for field in self.section_schemas[section]:
                    if field not in config[section]:
                        errors.append(f"Missing {section}.{field}")

        return errors

    def is_valid(self, config: Dict[str, Any]) -> bool:
        """Quick validation check"""
        return len(self.validate(config)) == 0
