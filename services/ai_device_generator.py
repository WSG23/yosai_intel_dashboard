"""
AI-powered device attribute generation service.
Extracted from door_mapping_service.py for modularity.
"""
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import pandas as pd
import logging

@dataclass
class DeviceAttributes:
    """AI-generated device attributes."""
    device_id: str
    device_name: str
    floor_number: int
    security_level: int
    is_entry: bool
    is_exit: bool
    is_elevator: bool
    is_stairwell: bool
    is_fire_escape: bool
    confidence: float
    ai_reasoning: str

class AIDeviceGenerator:
    """Consolidated AI device attribute generator."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Floor extraction patterns
        self.floor_patterns = [
            (r'[Ll](\d+)', lambda m: int(m.group(1))),  # L1, l2
            (r'[Ff]loor.*?(\d+)', lambda m: int(m.group(1))),  # floor_3
            (r'(\d+)[Ff]', lambda m: int(m.group(1))),  # 2F, 3f
            (r'^(\d+)_', lambda m: int(m.group(1))),  # 1_door
            (r'_(\d+)_', lambda m: int(m.group(1))),  # office_2_door
        ]

        # Security level patterns (pattern -> level)
        self.security_patterns = {
            r'lobby|reception|public|entrance': 2,
            r'office|desk|workspace|room_\d+': 4,
            r'meeting|conference|boardroom': 5,
            r'server|data|it|network': 8,
            r'executive|ceo|president|admin': 7,
            r'secure|restricted|vault|safe': 9,
            r'emergency|fire|safety': 6,
            r'elevator|lift': 3,
            r'stair|stairs': 3
        }

        # Access type patterns
        self.access_patterns = {
            'entry': [r'entry|entrance|in|lobby|front'],
            'exit': [r'exit|egress|out|emergency|back'],
            'elevator': [r'elevator|lift|elev'],
            'stairwell': [r'stair|stairs|step'],
            'fire_escape': [r'fire|emergency.*exit|escape']
        }

    def generate_device_attributes(self, device_id: str,
                                   usage_data: Optional[pd.DataFrame] = None) -> DeviceAttributes:
        """Generate comprehensive device attributes using AI analysis."""
        device_lower = device_id.lower()
        reasoning_parts: List[str] = []

        # Extract floor number
        floor_num = self._extract_floor(device_id, reasoning_parts)

        # Calculate security level
        security_level = self._calculate_security_level(device_lower, reasoning_parts)

        # Determine access types
        access_flags = self._determine_access_types(device_lower, reasoning_parts)

        # Generate readable name
        device_name = self._generate_device_name(device_id, reasoning_parts)

        # Calculate confidence
        confidence = self._calculate_confidence(reasoning_parts)

        return DeviceAttributes(
            device_id=device_id,
            device_name=device_name,
            floor_number=floor_num,
            security_level=security_level,
            is_entry=access_flags['entry'],
            is_exit=access_flags['exit'],
            is_elevator=access_flags['elevator'],
            is_stairwell=access_flags['stairwell'],
            is_fire_escape=access_flags['fire_escape'],
            confidence=confidence,
            ai_reasoning="; ".join(reasoning_parts)
        )

    def _extract_floor(self, device_id: str, reasoning: List[str]) -> int:
        """Extract floor number using pattern matching."""
        for pattern, extractor in self.floor_patterns:
            match = re.search(pattern, device_id)
            if match:
                try:
                    floor = extractor(match)
                    reasoning.append(f"Floor {floor} detected from pattern")
                    return max(1, floor)
                except (ValueError, IndexError):
                    continue
        reasoning.append("Floor 1 (default - no pattern match)")
        return 1

    def _calculate_security_level(self, device_lower: str, reasoning: List[str]) -> int:
        """Calculate security level based on naming patterns."""
        for pattern, level in self.security_patterns.items():
            if re.search(pattern, device_lower):
                reasoning.append(f"Security level {level} from device type")
                return level
        reasoning.append("Security level 5 (default office)")
        return 5

    def _determine_access_types(self, device_lower: str, reasoning: List[str]) -> Dict[str, bool]:
        """Determine access type boolean flags."""
        flags = {access_type: False for access_type in self.access_patterns.keys()}
        for access_type, patterns in self.access_patterns.items():
            for pattern in patterns:
                if re.search(pattern, device_lower):
                    flags[access_type] = True
                    reasoning.append(f"Detected {access_type} access")
                    break
        return flags

    def _generate_device_name(self, device_id: str, reasoning: List[str]) -> str:
        """Generate human-readable device name."""
        name = re.sub(r'[_-]', ' ', device_id)
        name = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', name)
        name = ' '.join(word.capitalize() for word in name.split())
        reasoning.append("Generated readable name")
        return name

    def _calculate_confidence(self, reasoning: List[str]) -> float:
        """Calculate AI confidence based on successful pattern matches."""
        base_confidence = 0.5
        pattern_matches = len([r for r in reasoning if 'detected' in r or 'pattern' in r])
        confidence_boost = min(pattern_matches * 0.1, 0.4)
        return min(base_confidence + confidence_boost, 0.95)


def create_ai_device_generator() -> AIDeviceGenerator:
    """Factory function for AI device generator."""
    return AIDeviceGenerator()
