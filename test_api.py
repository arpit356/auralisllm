import requests
import json
import time
import os
import subprocess

BASE_URL = "http://localhost:8000"
HEADERS = {"X-API-KEY": "auralis_secret_key_2026"}

def check_ollama():
    """Checks if Ollama is running as it's the core engine."""
    try:
        output = subprocess.check_output('tasklist /FI "IMAGENAME eq ollama.exe"', shell=True).decode()
        if "ollama.exe" in output:
            print("[OK] Ollama Engine is running.")
            return True
        else:
            print("[!] WARNING: Ollama Engine is NOT detected in tasklist.")
            return False
    except:
        return False

def test_api():
    print("\n--- 1. Testing API Health ---")
    try:
        r = requests.get(f"{BASE_URL}/health")
        print(f"Status: {r.status_code}")
        print(f"Response: {json.dumps(r.json(), indent=2)}")
    except Exception as e:
        print(f"[ERROR] Health check failed: {e}")
        return

    print("\n--- 2. Testing Security Layer ---")
    try:
        r_no_key = requests.get(f"{BASE_URL}/memory")
        print(f"Access (No Key): {r_no_key.status_code} (Expected 401)")
        
        r_wrong_key = requests.get(f"{BASE_URL}/memory", headers={"X-API-KEY": "wrong_key"})
        print(f"Access (Wrong Key): {r_wrong_key.status_code} (Expected 401)")
    except Exception as e:
        print(f"[ERROR] Security test failed: {e}")

    print("\n--- 3. Testing AI Processing (Llama 3.2 3B) ---")
    payload = {
        "speaker": "Alice",
        "transcript": "Auralis, what are the privacy rules for this meeting?"
    }
    try:
        print(f"Sending transcript to {BASE_URL}/process...")
        start_time = time.time()
        r = requests.post(f"{BASE_URL}/process", json=payload, headers=HEADERS, timeout=130)
        duration = time.time() - start_time
        print(f"Status: {r.status_code} (Time: {duration:.2f}s)")
        if r.status_code == 200:
            print(f"AI Response:\n{json.dumps(r.json(), indent=2)}")
        else:
            print(f"Response Error: {r.text}")
    except Exception as e:
        print(f"[ERROR] Processing call failed: {e}")

    print("\n--- 4. Testing Meeting Memory ---")
    try:
        r = requests.get(f"{BASE_URL}/memory", headers=HEADERS)
        print(f"Memory Status: {r.status_code}")
        if r.status_code == 200:
            print(f"Current Memory:\n{json.dumps(r.json(), indent=2)}")
    except Exception as e:
        print(f"[ERROR] Memory check failed: {e}")

if __name__ == "__main__":
    print("=======================================")
    print("   AURALIS SYSTEM DIAGNOSTIC TOOL      ")
    print("=======================================")
    
    check_ollama()
    
    print(f"\nWaiting for Auralis API on {BASE_URL}...")
    server_up = False
    for i in range(15):
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=2)
            if r.status_code == 200:
                print(f"[OK] Auralis API (v{r.json().get('version', '1.2.0')}) is online!")
                server_up = True
                break
        except:
            pass
        time.sleep(2)
        print(".", end="", flush=True)
    
    if not server_up:
        print("\n[FAIL] Auralis API could not be reached. Please run 'python auralis_api.py' in another terminal.")
        import sys
        sys.exit(1)

    test_api()
    print("\n--- Diagnostic Complete ---")
