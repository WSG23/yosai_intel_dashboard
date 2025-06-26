# Create: test_regex.py
import re

def test_regex_patterns():
    """Test regex patterns directly"""
    
    devices = ['F01C Staircase C', 'F02A Staircase A', 'F03A Server 1']
    
    patterns = [
        (r'[Ff]0*(\d+)[A-Z]', 'Original pattern'),
        (r'^[Ff]0*(\d+)', 'Start of string pattern'),
        (r'[Ff](\d+)', 'Simple F + digits'),
        (r'[Ff]0(\d+)', 'F + 0 + digits'),
    ]
    
    for device in devices:
        print(f"\n🔍 Testing: '{device}'")
        for pattern, name in patterns:
            match = re.search(pattern, device)
            if match:
                print(f"   ✅ {name}: {pattern} → groups: {match.groups()}")
                try:
                    floor = int(match.group(1))
                    print(f"      Floor: {floor}")
                except:
                    print(f"      Error extracting floor")
            else:
                print(f"   ❌ {name}: {pattern} → no match")

if __name__ == "__main__":
    test_regex_patterns()