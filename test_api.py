import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api():
    print("--- Testing Auralis API Health ---")
    try:
        r = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {r.status_code} - {r.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return

    print("\n--- Testing Auralis API Processing ---")
    payload = {
        "speaker": "Alice",
        "transcript": "Auralis, what are the privacy rules for this meeting?"
    }
    try:
        r = requests.post(f"{BASE_URL}/process", json=payload)
        print(f"Process turn: {r.status_code}")
        print(json.dumps(r.json(), indent=2))
    except Exception as e:
        print(f"Process turn failed: {e}")

    print("\n--- Testing Auralis API Memory ---")
    try:
        r = requests.get(f"{BASE_URL}/memory")
        print(f"Check memory: {r.status_code}")
        print(json.dumps(r.json(), indent=2))
    except Exception as e:
        print(f"Check memory failed: {e}")

if __name__ == "__main__":
    # Wait a few seconds for the server to be ready
    print("Waiting for server to fully initialize...")
    time.sleep(5)
    test_api()
