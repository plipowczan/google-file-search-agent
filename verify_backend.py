import requests
import time
import os

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing Health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✓ Health Check Passed")
        else:
            print(f"✗ Health Check Failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Health Check Failed: {e}")

def test_create_store(name):
    print(f"Testing Create Store '{name}'...")
    try:
        response = requests.post(f"{BASE_URL}/stores/", json={"display_name": name})
        if response.status_code == 201:
            print("✓ Create Store Passed")
            return response.json()
        elif response.status_code == 409:
            print("! Store already exists (Conflict)")
            # Try to find it
            stores = requests.get(f"{BASE_URL}/stores/").json()['stores']
            for s in stores:
                if s['display_name'] == name:
                    return s
        else:
            print(f"✗ Create Store Failed: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Create Store Failed: {e}")
        return None

def test_upload_file(store_id):
    print("Testing Upload File...")
    # Create dummy file
    with open("test_doc.txt", "w") as f:
        f.write("This is a test document for Gemini RAG Manager. It contains information about the project.")
    
    try:
        with open("test_doc.txt", "rb") as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/stores/{store_id}/files/", files=files)
        
        if response.status_code == 201:
            print("✓ Upload File Passed")
            return response.json()
        else:
            print(f"✗ Upload File Failed: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Upload File Failed: {e}")
        return None
    finally:
        if os.path.exists("test_doc.txt"):
            os.remove("test_doc.txt")

def test_chat(store_id):
    print("Testing Chat...")
    try:
        response = requests.post(f"{BASE_URL}/chat/", json={
            "store_id": store_id,
            "message": "What is this document about?"
        })
        if response.status_code == 200:
            print("✓ Chat Passed")
            print(f"  Response: {response.json()['response'][:100]}...")
        else:
            print(f"✗ Chat Failed: {response.text}")
    except Exception as e:
        print(f"✗ Chat Failed: {e}")

def main():
    test_health()
    store = test_create_store("Verification Store")
    if store:
        file = test_upload_file(store['id'])
        if file:
            # Wait for indexing?
            print("Waiting 5s for indexing...")
            time.sleep(5)
            test_chat(store['id'])
        
        # Cleanup
        # print("Cleaning up...")
        # requests.delete(f"{BASE_URL}/stores/{store['id']}")

if __name__ == "__main__":
    main()
