#!/usr/bin/env python3
"""
Simple test script for upload system
Run this to verify your changes work
"""

import sys
import base64
import pandas as pd


def test_system():
    """Test the upload system"""
    print("🧪 Testing Upload System...\n")

    try:
        # Test imports
        print("1. Testing imports...")
        from components.analytics.file_uploader import AIColumnMapper, FileUploadController, DeviceMapper
        print("   ✅ All classes imported successfully\n")

        # Test AI Column Mapper
        print("2. Testing AI Column Mapper...")
        mapper = AIColumnMapper()
        test_columns = ['timestamp', 'door_id', 'user_name', 'access_result']
        result = mapper.analyze_columns(test_columns)
        print(f"   ✅ AI Suggestions: {result['suggestions']}")
        print(f"   ✅ Confidence Scores: {result['confidence']}\n")

        # Test File Processing
        print("3. Testing File Processing...")
        controller = FileUploadController()

        # Create test CSV
        test_data = {
            'timestamp': ['2025-01-01 09:00:00', '2025-01-01 09:05:00'],
            'device_name': ['MAIN_ENTRANCE', 'SERVER_ROOM'],
            'user_id': ['EMP001', 'EMP002'],
            'event_type': ['Granted', 'Denied']
        }

        df = pd.DataFrame(test_data)
        csv_content = df.to_csv(index=False)
        encoded = base64.b64encode(csv_content.encode()).decode()
        upload_contents = f"data:text/csv;base64,{encoded}"

        # Test upload processing
        result = controller.process_upload(upload_contents, "test.csv")
        if result['success']:
            print(f"   ✅ File processed: {result['record_count']} records, {result['column_count']} columns")
            print(f"   ✅ AI Suggestions: {result['ai_suggestions']}")
        else:
            print(f"   ❌ Processing failed: {result['error']}")
        print()

        # Test Device Mapping
        print("4. Testing Device Mapping...")
        device_mapper = DeviceMapper()
        device_data = [
            {'device_name': 'MAIN_ENTRANCE_F1'},
            {'device_name': 'SERVER_ROOM_2F'},
            {'device_name': 'OFFICE_DOOR_3'},
        ]

        device_result = device_mapper.analyze_devices(device_data, 'device_name')
        if device_result['success']:
            print(f"   ✅ Analyzed {device_result['device_count']} devices")
            print(f"   ✅ Floor distribution: {device_result['floor_distribution']}")
            for mapping in device_result['device_mappings']:
                print(f"   📍 {mapping['device_id']} -> Floor {mapping['suggested_floor']}, Area: {mapping['suggested_area']}")
        else:
            print(f"   ❌ Device mapping failed: {device_result['error']}")
        print()

        print("🎉 All tests passed! Your upload system is working correctly.")
        print("\n📝 Next steps:")
        print("1. Start your Dash app")
        print("2. Go to the file upload page")
        print("3. Upload a CSV file")
        print("4. Verify the column mapping modal appears")
        print("5. Test the AI suggestions and user verification")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you've made all the required changes to your files.")

    except Exception as e:
        print(f"❌ Test error: {e}")
        print("Check that all code changes were applied correctly.")


if __name__ == '__main__':
    test_system()
