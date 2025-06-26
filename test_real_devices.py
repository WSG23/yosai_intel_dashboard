# Create: test_real_devices.py
from services.ai_device_generator import AIDeviceGenerator

def test_real_device_names():
    """Test AI with your actual device names"""
    
    real_devices = [
        'F01C Staircase C',
        'F01A Telecom room 2', 
        'F01A Gate 5 exit',
        'F01A Gate 5 entry',
        'F02A Staircase A',
        'F02A Security camera room',
        'F03A Staircase A to Corner office (TRK)',
        'F03A Staircase A to Office', 
        'F03A Server 1',
        'F03A Server 2'
    ]
    
    ai_gen = AIDeviceGenerator()
    
    print("🧪 Testing Enhanced AI on Real Device Names")
    print("=" * 60)
    
    for device in real_devices:
        result = ai_gen.generate_device_attributes(device)
        
        print(f"\n🚪 Device: '{device}'")
        print(f"   📝 AI Name: '{result.device_name}'")
        print(f"   🏢 Floor: {result.floor_number}")
        print(f"   🔒 Security: {result.security_level}")
        print(f"   📊 Confidence: {result.confidence:.1%}")
        print(f"   🚪 Access: Entry={result.is_entry}, Exit={result.is_exit}, Elevator={result.is_elevator}, Stairwell={result.is_stairwell}")
        print(f"   🧠 Reasoning: {result.ai_reasoning}")

if __name__ == "__main__":
    test_real_device_names()