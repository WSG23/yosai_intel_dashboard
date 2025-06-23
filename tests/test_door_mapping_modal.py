import pytest
from dash import html

from components.door_mapping_modal import create_device_mapping_table


def test_create_device_mapping_table_with_strings() -> None:
    devices = ["DEV1", "DEV2"]
    table = create_device_mapping_table(devices)
    assert isinstance(table, html.Table)
    assert len(table.children[1].children) == 2


def test_create_device_mapping_table_with_dicts() -> None:
    devices = [{"device_id": "DEV1", "location": "L1", "critical": True, "security_level": 80}]
    table = create_device_mapping_table(devices)
    assert isinstance(table, html.Table)
    assert len(table.children[1].children) == 1

