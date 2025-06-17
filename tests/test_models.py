# test_models.py
from models import AccessEvent, Person, AnomalyDetection
from models.enums import AccessResult, AnomalyType, SeverityLevel
from datetime import datetime

# Test creating entities
person = Person(person_id="EMP001", name="Test User")
print(f"Created person: {person.person_id}")

event = AccessEvent(
    event_id="TEST001",
    timestamp=datetime.now(),
    person_id="EMP001", 
    door_id="MAIN",
    access_result=AccessResult.GRANTED
)
print(f"Created event: {event.to_dict()}")

anomaly = AnomalyDetection(
    anomaly_id="ANOM001",
    event_id="TEST001",
    anomaly_type=AnomalyType.ODD_TIME,
    severity=SeverityLevel.MEDIUM,
    confidence_score=0.75,
    description="Access outside normal hours",
    detected_at=datetime.now()
)
print(f"Created anomaly: {anomaly.to_dict()}")

print("✓ All models working correctly!")