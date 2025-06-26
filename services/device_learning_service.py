import json
import hashlib
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

class DeviceLearningService:
    """Persistent device mapping learning service"""

    def __init__(self):
        self.storage_dir = Path("data/device_learning")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.learned_mappings = {}
        self._load_all_learned_mappings()

    def _get_file_fingerprint(self, df: pd.DataFrame, filename: str) -> str:
        """Create unique fingerprint for file based on structure and content sample"""
        fingerprint_data = {
            'filename': filename.split('.')[0],
            'columns': sorted(df.columns.tolist()),
            'shape': df.shape,
            'sample_devices': sorted(df[self._find_device_column(df)].dropna().unique()[:5].tolist()) if self._find_device_column(df) else []
        }
        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.md5(fingerprint_str.encode()).hexdigest()[:12]

    def _find_device_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find the device/door column in the dataframe"""
        device_columns = [col for col in df.columns 
                         if any(keyword in col.lower() 
                               for keyword in ['device', 'door', 'location', 'area', 'room'])]
        return device_columns[0] if device_columns else None

    def _load_all_learned_mappings(self):
        """Load all learned mappings from storage"""
        try:
            for mapping_file in self.storage_dir.glob("mapping_*.json"):
                try:
                    with open(mapping_file, 'r') as f:
                        data = json.load(f)
                        fingerprint = mapping_file.stem.replace("mapping_", "")
                        self.learned_mappings[fingerprint] = data
                    logger.info(f"Loaded learned mapping: {fingerprint}")
                except Exception as e:
                    logger.warning(f"Failed to load mapping file {mapping_file}: {e}")
        except Exception as e:
            logger.error(f"Failed to load learned mappings: {e}")

    def save_device_mappings(self, df: pd.DataFrame, filename: str, device_mappings: Dict[str, Dict]) -> str:
        """Save device mappings for future use"""
        try:
            fingerprint = self._get_file_fingerprint(df, filename)
            learning_data = {
                'fingerprint': fingerprint,
                'filename': filename,
                'learned_at': datetime.now().isoformat(),
                'device_count': len(device_mappings),
                'mappings': device_mappings,
                'file_info': {
                    'columns': df.columns.tolist(),
                    'shape': df.shape,
                    'device_column': self._find_device_column(df)
                }
            }
            mapping_file = self.storage_dir / f"mapping_{fingerprint}.json"
            with open(mapping_file, 'w') as f:
                json.dump(learning_data, f, indent=2)
            self.learned_mappings[fingerprint] = learning_data
            logger.info(f"Saved device mappings for {filename} (fingerprint: {fingerprint})")
            return fingerprint
        except Exception as e:
            logger.error(f"Failed to save device mappings: {e}")
            return ""

    def get_learned_mappings(self, df: pd.DataFrame, filename: str) -> Optional[Dict[str, Dict]]:
        """Get learned mappings for this file if they exist"""
        try:
            fingerprint = self._get_file_fingerprint(df, filename)
            if fingerprint in self.learned_mappings:
                learned_data = self.learned_mappings[fingerprint]
                logger.info(f"Found learned mappings for {filename} (fingerprint: {fingerprint})")
                return learned_data['mappings']
            for fp, data in self.learned_mappings.items():
                if data['filename'].split('.')[0] == filename.split('.')[0]:
                    logger.info(f"Found similar file mappings for {filename}")
                    return data['mappings']
            return None
        except Exception as e:
            logger.error(f"Failed to get learned mappings: {e}")
            return None

    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of all learned mappings"""
        return {
            'total_learned_files': len(self.learned_mappings),
            'files': [
                {
                    'filename': data['filename'],
                    'learned_at': data['learned_at'],
                    'device_count': data['device_count']
                }
                for data in self.learned_mappings.values()
            ]
        }

_device_learning_service = DeviceLearningService()

def get_device_learning_service() -> DeviceLearningService:
    return _device_learning_service
