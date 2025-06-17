# test_models.py
"""
Quick test script to verify all models are working correctly
Place this file in your project root directory (same level as app.py)
"""

import sys
import os
from datetime import datetime
import uuid

def test_imports():
    """Test if all model imports work"""
    print("🧪 Testing model imports...")
    
    try:
        from models.enums import AccessResult, AnomalyType, SeverityLevel, BadgeStatus
        print("✅ Enums imported successfully")
        
        from models.entities import Person, Door, Facility
        print("✅ Entities imported successfully")
        
        from models.events import AccessEvent, AnomalyDetection, IncidentTicket
        print("✅ Events imported successfully")
        
        from models import ModelFactory
        print("✅ Factory imported successfully")
        
        # Test the convenience imports
        from models import AccessEvent as AE, Person as P
        print("✅ Convenience imports working")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("💡 Make sure all model files are created in the models/ directory")
        return False

def test_entity_creation():
    """Test creating entity objects"""
    print("\n👤 Testing entity creation...")
    
    try:
        from models.entities import Person, Door, Facility
        from models.enums import DoorType
        
        # Test Person creation
        person = Person(
            person_id="EMP001",
            name="Test User",
            department="Security",
            clearance_level=3
        )
        print(f"✅ Created person: {person.name} (ID: {person.person_id})")
        
        # Test Door creation
        door = Door(
            door_id="MAIN_ENTRANCE",
            door_name="Main Building Entrance",
            facility_id="HQ_TOWER",
            area_id="LOBBY",
            door_type=DoorType.STANDARD
        )
        print(f"✅ Created door: {door.door_name} (Type: {door.door_type.value})")
        
        # Test Facility creation
        facility = Facility(
            facility_id="HQ_TOWER",
            facility_name="Headquarters Tower",
            timezone="America/New_York"
        )
        print(f"✅ Created facility: {facility.facility_name}")
        
        # Test serialization
        person_dict = person.to_dict()
        print(f"✅ Person serialization: {len(person_dict)} fields")
        
        return True
        
    except Exception as e:
        print(f"❌ Entity creation failed: {e}")
        return False

def test_event_creation():
    """Test creating event objects"""
    print("\n⚡ Testing event creation...")
    
    try:
        from models.events import AccessEvent, AnomalyDetection, IncidentTicket
        from models.enums import AccessResult, BadgeStatus, AnomalyType, SeverityLevel, TicketStatus
        
        # Test AccessEvent creation
        event = AccessEvent(
            event_id=f"EVT_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(),
            person_id="EMP001",
            door_id="MAIN_ENTRANCE",
            access_result=AccessResult.GRANTED,
            badge_status=BadgeStatus.VALID
        )
        print(f"✅ Created access event: {event.event_id} ({event.access_result.value})")
        
        # Test AnomalyDetection creation
        anomaly = AnomalyDetection(
            anomaly_id=f"ANOM_{uuid.uuid4().hex[:8]}",
            event_id=event.event_id,
            anomaly_type=AnomalyType.ODD_TIME,
            severity=SeverityLevel.MEDIUM,
            confidence_score=0.75,
            description="Access outside normal business hours",
            detected_at=datetime.now()
        )
        print(f"✅ Created anomaly: {anomaly.anomaly_type.value} (Confidence: {anomaly.confidence_score})")
        
        # Test IncidentTicket creation
        ticket = IncidentTicket(
            ticket_id=f"TKT_{uuid.uuid4().hex[:8]}",
            event_id=event.event_id,
            anomaly_id=anomaly.anomaly_id,
            status=TicketStatus.NEW,
            threat_score=65,
            facility_location="HQ Tower East",
            area="Main Lobby"
        )
        print(f"✅ Created incident ticket: {ticket.ticket_id} (Threat: {ticket.threat_score}/100)")
        
        # Test serialization
        event_dict = event.to_dict()
        anomaly_dict = anomaly.to_dict()
        ticket_dict = ticket.to_dict()
        
        print(f"✅ Event serialization: {len(event_dict)} fields")
        print(f"✅ Anomaly serialization: {len(anomaly_dict)} fields")
        print(f"✅ Ticket serialization: {len(ticket_dict)} fields")
        
        return True
        
    except Exception as e:
        print(f"❌ Event creation failed: {e}")
        return False

def test_enums():
    """Test enum functionality"""
    print("\n📋 Testing enum functionality...")
    
    try:
        from models.enums import AnomalyType, AccessResult, SeverityLevel
        
        # Test enum values
        print(f"✅ Access results: {[result.value for result in AccessResult]}")
        print(f"✅ Severity levels: {[level.value for level in SeverityLevel]}")
        
        # Test enum comparison
        high_severity = SeverityLevel.HIGH
        critical_severity = SeverityLevel.CRITICAL
        
        if high_severity != critical_severity:
            print("✅ Enum comparison working")
        
        # Test enum in conditions
        test_severity = SeverityLevel.CRITICAL
        if test_severity == SeverityLevel.CRITICAL:
            print("✅ Enum conditionals working")
        
        # Show all anomaly types (from your PRD)
        print(f"✅ Available anomaly types: {len(list(AnomalyType))} types")
        for anomaly_type in list(AnomalyType)[:5]:  # Show first 5
            print(f"   • {anomaly_type.value}")
        print(f"   ... and {len(list(AnomalyType)) - 5} more")
        
        return True
        
    except Exception as e:
        print(f"❌ Enum testing failed: {e}")
        return False

def test_workflow_integration():
    """Test a complete workflow using all models together"""
    print("\n🔄 Testing complete workflow...")
    
    try:
        from models import AccessEvent, Person, AnomalyDetection, IncidentTicket
        from models.enums import AccessResult, AnomalyType, SeverityLevel, TicketStatus
        
        # 1. Create a person
        person = Person(person_id="EMP999", name="Security Test User")
        
        # 2. Simulate an access event
        event = AccessEvent(
            event_id="WORKFLOW_TEST_001",
            timestamp=datetime.now(),
            person_id=person.person_id,
            door_id="SERVER_ROOM",
            access_result=AccessResult.GRANTED
        )
        
        # 3. AI detects anomaly
        anomaly = AnomalyDetection(
            anomaly_id="WORKFLOW_ANOM_001",
            event_id=event.event_id,
            anomaly_type=AnomalyType.ODD_TIME,
            severity=SeverityLevel.HIGH,
            confidence_score=0.89,
            description=f"Server room access by {person.name} at unusual hour",
            detected_at=datetime.now()
        )
        
        # 4. Create incident ticket
        ticket = IncidentTicket(
            ticket_id="WORKFLOW_TKT_001",
            event_id=event.event_id,
            anomaly_id=anomaly.anomaly_id,
            status=TicketStatus.NEW,
            threat_score=75
        )
        
        # 5. Simulate workflow progression
        print(f"   📝 {person.name} accessed {event.door_id}")
        print(f"   🚨 AI detected: {anomaly.anomaly_type.value} (confidence: {anomaly.confidence_score:.0%})")
        print(f"   🎫 Created ticket: {ticket.ticket_id} (threat level: {ticket.threat_score}/100)")
        
        # 6. Test data conversion for database/API
        workflow_data = {
            'person': person.to_dict(),
            'event': event.to_dict(),
            'anomaly': anomaly.to_dict(),
            'ticket': ticket.to_dict()
        }
        
        print(f"✅ Workflow integration successful - {len(workflow_data)} components")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow integration failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 YŌSAI INTEL MODELS - QUICK TEST")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Entity Creation", test_entity_creation),
        ("Event Creation", test_event_creation),
        ("Enum Functionality", test_enums),
        ("Workflow Integration", test_workflow_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"⚠️  {test_name} had issues")
        except Exception as e:
            print(f"💥 {test_name} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Your models are working perfectly!")
        print("\n✅ Ready for:")
        print("   • Analytics page integration")
        print("   • Dashboard component updates") 
        print("   • Database persistence")
        print("   • AI anomaly detection")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        print("\n🔧 Common fixes:")
        print("   • Make sure all model files exist in models/ directory")
        print("   • Check for typos in file names")
        print("   • Verify __init__.py files are created")
        print("   • Ensure proper indentation in Python files")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🚀 Next steps:")
        print("   1. Run your app: python app.py")
        print("   2. Test analytics page: http://127.0.0.1:8050/analytics")
        print("   3. Try uploading sample data")
    
    sys.exit(0 if success else 1)