"""
Door Mapping Service - Business logic for device attribute assignment
Handles AI model data processing and manual override management
"""
import pandas as pd
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DeviceAttributeData:
    """Device attribute data structure"""
    door_id: str
    name: str
    entry: bool = False
    exit: bool = False
    elevator: bool = False
    stairwell: bool = False
    fire_escape: bool = False
    other: bool = False
    security_level: int = 50
    confidence: Optional[int] = None
    ai_generated: bool = True
    manually_edited: bool = False
    edit_timestamp: Optional[datetime] = None


class DoorMappingService:
    """Service for handling door mapping and device attribute assignment"""
    
    def __init__(self):
        self.ai_model_version = "v2.3"
        self.confidence_threshold = 75
        
    def process_uploaded_data(self, df: pd.DataFrame, client_profile: str = "auto") -> Dict[str, Any]:
        """
        Process uploaded CSV/JSON/Excel data and generate device attribute assignments
        
        Args:
            df: Uploaded data as pandas DataFrame
            client_profile: Client configuration profile
            
        Returns:
            Dict containing processed device data and metadata
        """
        try:
            # Validate required columns
            required_columns = ['door_id']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Extract unique devices
            unique_doors = df['door_id'].unique()
            
            # Generate AI attribute assignments
            devices_data = []
            for door_id in unique_doors:
                device_data = self._generate_ai_attributes(door_id, df, client_profile)
                devices_data.append(device_data)
            
            # Prepare response
            response = {
                'devices': [device.__dict__ for device in devices_data],
                'metadata': {
                    'total_devices': len(devices_data),
                    'ai_model_version': self.ai_model_version,
                    'client_profile': client_profile,
                    'processing_timestamp': datetime.now().isoformat(),
                    'confidence_threshold': self.confidence_threshold
                }
            }
            
            logger.info(f"Processed {len(devices_data)} devices for door mapping")
            return response
            
        except Exception as e:
            logger.error(f"Error processing uploaded data: {e}")
            raise
    
    def _generate_ai_attributes(self, door_id: str, df: pd.DataFrame, client_profile: str) -> DeviceAttributeData:
        """
        Generate AI-based attribute assignments for a device
        
        Args:
            door_id: Device identifier
            df: Source data
            client_profile: Client configuration
            
        Returns:
            DeviceAttributeData with AI-generated attributes
        """
        # Get device-specific data
        device_rows = df[df['door_id'] == door_id]
        
        # Generate device name (clean up door_id)
        device_name = self._generate_device_name(door_id, device_rows)
        
        # AI logic for attribute assignment based on door_id patterns
        attributes = self._analyze_door_patterns(door_id, device_rows, client_profile)
        
        # Calculate confidence score
        confidence = self._calculate_confidence_score(door_id, attributes, device_rows)
        
        return DeviceAttributeData(
            door_id=door_id,
            name=device_name,
            entry=attributes.get('entry', False),
            exit=attributes.get('exit', False),
            elevator=attributes.get('elevator', False),
            stairwell=attributes.get('stairwell', False),
            fire_escape=attributes.get('fire_escape', False),
            other=attributes.get('other', False),
            security_level=attributes.get('security_level', 50),
            confidence=confidence,
            ai_generated=True,
            manually_edited=False
        )
    
    def _generate_device_name(self, door_id: str, device_rows: pd.DataFrame) -> str:
        """Generate a human-readable device name"""
        # Clean up door_id and make it more readable
        name = door_id.replace('_', ' ').replace('-', ' ')
        
        # Capitalize words
        name = ' '.join(word.capitalize() for word in name.split())
        
        # Add context if available from data
        if len(device_rows) > 0:
            # Check for common patterns in access data
            if any('entry' in str(device_rows.iloc[0]).lower() for _ in [True]):
                pass  # Keep name as is
        
        return name
    
    def _analyze_door_patterns(self, door_id: str, device_rows: pd.DataFrame, client_profile: str) -> Dict[str, Any]:
        """
        Analyze door ID patterns to determine likely attributes
        
        This is where the AI model logic would go. For now, using rule-based patterns.
        """
        door_id_lower = door_id.lower()
        attributes = {
            'entry': False,
            'exit': False,
            'elevator': False,
            'stairwell': False,
            'fire_escape': False,
            'other': False,
            'security_level': 50
        }
        
        # Pattern matching for door types
        if any(keyword in door_id_lower for keyword in ['entry', 'entrance', 'front', 'main']):
            attributes['entry'] = True
            attributes['security_level'] = 70
            
        if any(keyword in door_id_lower for keyword in ['exit', 'back', 'rear', 'emergency']):
            attributes['exit'] = True
            attributes['security_level'] = 60
            
        if any(keyword in door_id_lower for keyword in ['elevator', 'lift', 'elev']):
            attributes['elevator'] = True
            attributes['security_level'] = 40
            
        if any(keyword in door_id_lower for keyword in ['stair', 'stairwell', 'stairs']):
            attributes['stairwell'] = True
            attributes['security_level'] = 55
            
        if any(keyword in door_id_lower for keyword in ['fire', 'emergency', 'escape']):
            attributes['fire_escape'] = True
            attributes['security_level'] = 80
            
        # If no specific pattern matched, mark as other
        if not any(attributes[key] for key in ['entry', 'exit', 'elevator', 'stairwell', 'fire_escape']):
            attributes['other'] = True
            
        # Adjust security levels based on client profile
        if client_profile == "high_security":
            attributes['security_level'] = min(100, attributes['security_level'] + 20)
        elif client_profile == "low_security":
            attributes['security_level'] = max(0, attributes['security_level'] - 20)
            
        return attributes
    
    def _calculate_confidence_score(self, door_id: str, attributes: Dict[str, Any], device_rows: pd.DataFrame) -> int:
        """Calculate confidence score for AI-generated attributes"""
        confidence = 50  # Base confidence
        
        # Increase confidence for clear patterns
        door_id_lower = door_id.lower()
        clear_patterns = ['entry', 'exit', 'elevator', 'stair', 'fire', 'emergency']
        
        for pattern in clear_patterns:
            if pattern in door_id_lower:
                confidence += 15
                
        # Increase confidence based on data volume
        if len(device_rows) > 100:
            confidence += 10
        elif len(device_rows) > 50:
            confidence += 5
            
        # Cap at 95% (never 100% to indicate AI uncertainty)
        return min(95, confidence)
    
    def apply_manual_edits(self, original_data: List[Dict], manual_edits: Dict[str, Dict]) -> List[Dict]:
        """
        Apply manual edits to device data
        
        Args:
            original_data: Original AI-generated device data
            manual_edits: Manual edits per device
            
        Returns:
            Updated device data with manual edits applied
        """
        updated_data = []
        
        for device in original_data:
            device_id = device['door_id']
            
            # Create a copy of the device data
            updated_device = device.copy()
            
            # Apply manual edits if they exist
            if device_id in manual_edits:
                edits = manual_edits[device_id]
                
                # Update attributes
                for attr, value in edits.items():
                    if attr in updated_device:
                        updated_device[attr] = value
                        
                # Mark as manually edited
                updated_device['manually_edited'] = True
                updated_device['edit_timestamp'] = datetime.now().isoformat()
                updated_device['confidence'] = None  # Clear AI confidence for manual edits
                
            updated_data.append(updated_device)
            
        return updated_data

    def save_verified_mapping(self, mapping_data: Dict[str, Any], user_id: str) -> bool:
        """
        Save verified column mapping for future use

        Args:
            mapping_data: Verified mapping configuration
            user_id: User identifier

        Returns:
            Success status
        """
        try:
            mapping_record = {
                'user_id': user_id,
                'timestamp_col': mapping_data.get('timestamp'),
                'device_col': mapping_data.get('device_name'),
                'user_col': mapping_data.get('token_id'),
                'event_type_col': mapping_data.get('event_type'),
                'floor_estimate': mapping_data.get('floors', 1),
                'verified_at': datetime.now().isoformat(),
                'ai_model_version': self.ai_model_version
            }

            # Store in your preferred storage system
            # This could be database, file, or cache depending on your setup
            logger.info(f"Saved verified mapping for user {user_id}: {mapping_record}")

            return True

        except Exception as e:
            logger.error(f"Error saving verified mapping: {e}")
            return False
    
    def save_manual_edits_for_training(self, manual_edits: Dict[str, Dict], original_data: List[Dict]):
        """
        Save manual edits to improve AI model training
        
        This would typically save to a training database for model improvement
        """
        try:
            training_data = {
                'timestamp': datetime.now().isoformat(),
                'ai_model_version': self.ai_model_version,
                'manual_edits': manual_edits,
                'original_ai_predictions': original_data,
                'edit_count': len(manual_edits)
            }
            
            # Here you would save to your training database
            # For now, just log the information
            logger.info(f"Saved {len(manual_edits)} manual edits for AI training")
            
            return training_data
            
        except Exception as e:
            logger.error(f"Error saving manual edits for training: {e}")
            raise


# Service instance
door_mapping_service = DoorMappingService()

__all__ = ["DoorMappingService", "DeviceAttributeData", "door_mapping_service"]
