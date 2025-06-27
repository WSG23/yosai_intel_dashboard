# Add to your app.py or create debug_learning.py
from services.consolidated_learning_service import get_learning_service

def check_learning_status():
    """Check current learning status"""
    service = get_learning_service()
    stats = service.get_learning_statistics()
    
    print("🧠 LEARNING STATUS:")
    print(f"   Total learned files: {stats['total_mappings']}")
    print(f"   Total devices learned: {stats['total_devices']}")
    print(f"   Latest save: {stats.get('latest_save', 'None')}")
    
    print("\n📁 LEARNED FILES:")
    for file_info in stats['files']:
        print(f"   • {file_info['filename']} - {file_info['device_count']} devices")
        print(f"     Fingerprint: {file_info['fingerprint']}")
        print(f"     Saved: {file_info['saved_at']}")
    
    # Check if storage file exists
    import os
    storage_exists = os.path.exists("data/learned_mappings.pkl")
    print(f"\n💾 Storage file exists: {storage_exists}")
    
    if storage_exists:
        file_size = os.path.getsize("data/learned_mappings.pkl")
        print(f"   File size: {file_size} bytes")

# Run this after testing
if __name__ == "__main__":
    check_learning_status()