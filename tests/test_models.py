from datetime import datetime

from models import AccessEvent, AnomalyDetection, Person
from models.enums import AccessResult, AnomalyType, SeverityLevel


def test_model_creation() -> None:
    person = Person(person_id="EMP001", name="Test User")
    assert person.person_id == "EMP001"

    event = AccessEvent(
        event_id="TEST001",
        timestamp=datetime.now(),
        person_id=person.person_id,
        door_id="MAIN",
        access_result=AccessResult.GRANTED,
    )
    assert event.person_id == person.person_id

    anomaly = AnomalyDetection(
        anomaly_id="ANOM001",
        event_id=event.event_id,
        anomaly_type=AnomalyType.ODD_TIME,
        severity=SeverityLevel.MEDIUM,
        confidence_score=0.75,
        description="Access outside normal hours",
        detected_at=datetime.now(),
    )
    assert anomaly.event_id == event.event_id
