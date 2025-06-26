"""
Test suite for AI device generator module.
"""
import pytest
from services.ai_device_generator import AIDeviceGenerator

class TestAIDeviceGenerator:

    def setup_method(self):
        self.generator = AIDeviceGenerator()

    def test_floor_extraction_patterns(self):
        test_cases = [
            ("lobby_L1_door", 1),
            ("office_3F_main", 3),
            ("floor_2_entrance", 2),
            ("5_server_room", 5),
            ("basement_door", 1),
            ("office_201_door", 2),
        ]
        for device_id, expected in test_cases:
            attrs = self.generator.generate_device_attributes(device_id)
            assert attrs.floor_number == expected

    def test_security_level_detection(self):
        test_cases = [
            ("lobby_entrance", 2),
            ("office_201", 4),
            ("server_room_door", 8),
            ("executive_suite", 7),
            ("elevator_1", 3),
            ("vault_door", 9),
        ]
        for device_id, expected in test_cases:
            attrs = self.generator.generate_device_attributes(device_id)
            assert attrs.security_level == expected

    def test_access_type_detection(self):
        test_cases = [
            ("main_entrance", True, False, False),
            ("emergency_exit", False, True, False),
            ("elevator_1", False, False, True),
            ("fire_escape", False, True, False),
        ]
        for device_id, expect_entry, expect_exit, expect_elevator in test_cases:
            attrs = self.generator.generate_device_attributes(device_id)
            assert attrs.is_entry == expect_entry
            assert attrs.is_exit == expect_exit
            assert attrs.is_elevator == expect_elevator

    def test_device_name_generation(self):
        test_cases = [
            ("lobby_L1_door", "Lobby L1 Door"),
            ("office_201", "Office 201"),
            ("server-room_3F", "Server Room 3 F"),
        ]
        for device_id, expected_name in test_cases:
            attrs = self.generator.generate_device_attributes(device_id)
            assert attrs.device_name == expected_name

    def test_confidence_calculation(self):
        clear_attrs = self.generator.generate_device_attributes("office_3F_entrance")
        unclear_attrs = self.generator.generate_device_attributes("device_123")
        assert clear_attrs.confidence > unclear_attrs.confidence
        assert 0.5 <= clear_attrs.confidence <= 0.95
        assert 0.5 <= unclear_attrs.confidence <= 0.95

    def test_ai_reasoning_output(self):
        attrs = self.generator.generate_device_attributes("office_2F_door")
        assert attrs.ai_reasoning
        assert "Floor" in attrs.ai_reasoning or "Security" in attrs.ai_reasoning
