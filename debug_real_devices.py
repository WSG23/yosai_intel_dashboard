# Create: debug_real_devices.py
import pandas as pd
from services.door_mapping_service import door_mapping_service

def debug_real_device_names():
    """Debug the actual device names in your uploaded file"""
    try:
        # Try to find your uploaded file
        # Update this path to wherever your uploaded files are stored
        file_path = "data/Demo3_data.csv"  # Adjust path as needed
        
        print("🔍 Loading Demo3_data.csv...")
        df = pd.read_csv(file_path)
        
        print(f"📊 File info:")
        print(f"   Rows: {len(df):,}")
        print(f"   Columns: {list(df.columns)}")
        
        # Find the device column
        device_col = None
        for col in df.columns:
            if 'device' in col.lower() or 'door' in col.lower():
                device_col = col
                break
        
        if not device_col:
            print("❌ No device column found!")
            return
        
        print(f"🎯 Device column: '{device_col}'")
        
        # Get unique device names
        unique_devices = df[device_col].unique()
        print(f"📱 Total unique devices: {len(unique_devices)}")
        
        # Show first 20 device names
        print(f"\n🏷️  First 20 device names:")
        for i, device in enumerate(unique_devices[:20]):
            print(f"   {i+1:2d}. {device}")
        
        # Test AI analysis on a few devices
        print(f"\n🤖 AI Analysis on sample devices:")
        
        # Create a test dataframe with correct column name
        test_df = pd.DataFrame({
            'door_id': unique_devices[:10]  # Use first 10 devices
        })
        
        debug_info = door_mapping_service.debug_device_names(test_df)
        
        for device, analysis in debug_info['ai_analysis'].items():
            print(f"\n🚪 Device: '{device}'")
            if 'error' in analysis:
                print(f"   ❌ Error: {analysis['error']}")
            else:
                print(f"   📝 Generated Name: {analysis.get('generated_name', 'N/A')}")
                print(f"   🏢 Floor: {analysis.get('floor', 'N/A')}")
                print(f"   🔒 Security Level: {analysis.get('security_level', 'N/A')}")
                print(f"   📊 Confidence: {analysis.get('confidence', 'N/A'):.1%}")
                print(f"   🧠 Reasoning: {analysis.get('reasoning', 'N/A')}")
                
                access_types = analysis.get('access_types', {})
                active_types = [k for k, v in access_types.items() if v]
                print(f"   🚪 Access Types: {active_types if active_types else 'None detected'}")
        
    except FileNotFoundError:
        print("❌ Demo3_data.csv not found!")
        print("Please upload the file first or update the file path in this script")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_real_device_names()
    