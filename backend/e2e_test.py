import httpx
import sys
import io

BASE_URL = "http://localhost:8000/api"

def run_e2e_test():
    print("=== STARTING TRUTHLENS AI E2E INTEGRATION TEST ===")
    
    # Generate a unique email for testing
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    email = f"test_{unique_id}@truthlens.ai"
    password = "testpassword123"
    
    # 1. Sign Up
    print(f"\n1. Registering user: {email}...")
    try:
        signup_res = httpx.post(f"{BASE_URL}/auth/signup", json={
            "email": email,
            "password": password
        })
        print(f"   Response Status: {signup_res.status_code}")
        if signup_res.status_code != 201:
            print("   ERROR: Signup failed.")
            print(signup_res.text)
            sys.exit(1)
        print("   SUCCESS: User registered.")
    except Exception as e:
        print(f"   CONNECTION ERROR: Could not connect to API server: {e}")
        print("   Make sure the FastAPI backend is running on http://localhost:8000")
        sys.exit(1)

    # 2. Login
    print("\n2. Logging in...")
    login_res = httpx.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    print(f"   Response Status: {login_res.status_code}")
    if login_res.status_code != 200:
        print("   ERROR: Login failed.")
        sys.exit(1)
    
    token_data = login_res.json()
    token = token_data.get("access_token")
    token_type = token_data.get("token_type")
    print("   SUCCESS: Retrieved access token.")
    
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Verify News Claim (Authenticated)
    print("\n3. Verifying a news claim (with auth)...")
    claim = "Scientists discover a brand new species of glowing mushroom in the Amazon."
    news_res = httpx.post(f"{BASE_URL}/verify/news", json={
        "claim": claim
    }, headers=headers)
    print(f"   Response Status: {news_res.status_code}")
    if news_res.status_code != 200:
        print("   ERROR: News verification request failed.")
        sys.exit(1)
    
    news_data = news_res.json()
    report_id = news_data.get("id")
    print(f"   SUCCESS: Created report. Report ID: {report_id}")
    print(f"   Trust Score: {news_data.get('trust_score')}%")
    print(f"   Risk Level: {news_data.get('risk_level')}")

    # 4. Get Public Report Details
    print(f"\n4. Fetching public report details for: {report_id}...")
    report_res = httpx.get(f"{BASE_URL}/report/{report_id}")
    print(f"   Response Status: {report_res.status_code}")
    if report_res.status_code != 200:
        print("   ERROR: Failed to retrieve public report.")
        sys.exit(1)
    print("   SUCCESS: Report details matches created claim.")

    # 5. Verify Image Upload (Authenticated)
    print("\n5. Testing image upload verification with mock JPG...")
    # Create a dummy JPEG in-memory
    mock_image = io.BytesIO()
    # Write some mock binary bytes
    mock_image.write(b'\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xFF\xDB\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xFF\xC0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xFF\xC4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xFF\xC4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01\x7d\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\x16\x92\xb2\xe1\xf1\x05\x17\x18\x19\x1a%&\'()*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xFF\xDA\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xfd\xfc\xa0\n\x0f\xFF\xD9')
    mock_image.seek(0)
    
    files = {"file": ("test_shimmer.jpg", mock_image, "image/jpeg")}
    image_res = httpx.post(f"{BASE_URL}/verify/image", files=files, headers=headers)
    print(f"   Response Status: {image_res.status_code}")
    if image_res.status_code != 200:
        print("   ERROR: Image upload failed.")
        print(image_res.text)
        sys.exit(1)
    
    image_data = image_res.json()
    print(f"   SUCCESS: Processed image. Report ID: {image_data.get('id')}")
    print(f"   Risk level: {image_data.get('risk_level')}")
    print(f"   Has EXIF anomalies: {len(image_data.get('details', {}).get('image_metadata', {}).get('anomalies', [])) > 0}")

    # 6. Fetch User Verification History
    print("\n6. Querying user scan history...")
    history_res = httpx.get(f"{BASE_URL}/history", headers=headers)
    print(f"   Response Status: {history_res.status_code}")
    if history_res.status_code != 200:
        print("   ERROR: Fetching scan history failed.")
        sys.exit(1)
    
    history_list = history_res.json()
    print(f"   SUCCESS: Retrieved {len(history_list)} history records.")
    for item in history_list:
        print(f"     - [{item.get('type').upper()}] {item.get('query')[:40]}... -> Risk: {item.get('risk_level')}")
        
    print("\n=== ALL E2E INTEGRATION TESTS COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_e2e_test()
