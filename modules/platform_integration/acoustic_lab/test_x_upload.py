#!/usr/bin/env python3
"""
Quick test script to verify X video upload functionality works after IP geofencing fix.
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===


import requests
import json

def test_x_upload():
    """Test X video upload with localhost bypass."""

    # Test data
    test_url = "https://x.com/example/status/123456789"  # Placeholder URL
    metadata = {
        "gps": {
            "latitude": 40.7649,
            "longitude": -111.8421
        },
        "timestamp": "2025-10-03T15:30:00Z"
    }

    # Test the upload endpoint
    url = "http://localhost:5000/upload"
    data = {
        'x_url': test_url,
        'metadata': json.dumps(metadata)
    }

    try:
        print("Testing X video upload...")
        response = requests.post(url, data=data, timeout=10)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("[SUCCESS] X video upload works!")
            print(f"Result: {result}")
        elif response.status_code == 403:
            print("[FAILED] Still getting 403 - IP geofencing not working")
            print(f"Response: {response.text}")
        elif response.status_code == 400:
            print("[EXPECTED] Got 400 (Bad Request) - likely invalid X URL")
            print("This is normal since we're using a placeholder URL")
            print("[OK] IP geofencing fix is working (no 403 error)")
        else:
            print(f"Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("[FAILED] Cannot connect to server - make sure it's running")
    except Exception as e:
        print(f"[FAILED] {e}")

if __name__ == "__main__":
    test_x_upload()
