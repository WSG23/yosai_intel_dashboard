import pandas as pd
from services.door_mapping_service import DoorMappingService


def test_process_uploaded_data_generates_attributes() -> None:
    df = pd.DataFrame({"door_id": ["MAIN_ENTRY", "SIDE_EXIT"]})
    service = DoorMappingService()
    result = service.process_uploaded_data(df)
    assert result["metadata"]["total_devices"] == 2
    ids = [d["door_id"] for d in result["devices"]]
    assert set(ids) == {"MAIN_ENTRY", "SIDE_EXIT"}


def test_confidence_score_bounds() -> None:
    df = pd.DataFrame({"door_id": ["ENTRY1"]})
    service = DoorMappingService()
    attrs = {"entry": True}
    score = service._calculate_confidence_score("ENTRY1", attrs, df)
    assert 0 <= score <= 95
