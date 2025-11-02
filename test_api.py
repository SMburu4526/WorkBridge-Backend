
import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_login():
    """Test login and get token"""
    data = {"username": "seeker1", "password": "password123"}
    response = requests.post(f"{BASE_URL}/login", json=data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✓ Login successful")
        return token
    else:
        print("✗ Login failed:", response.text)
        return None

def test_jobs():
    """Test job listings"""
    response = requests.get(f"{BASE_URL}/jobs")
    if response.status_code == 200:
        jobs = response.json()["jobs"]
        print(f"✓ Found {len(jobs)} jobs")
        return jobs[0]["id"] if jobs else None
    else:
        print("✗ Jobs fetch failed:", response.text)
        return None

def test_job_details(job_id):
    """Test job details"""
    response = requests.get(f"{BASE_URL}/jobs/{job_id}")
    if response.status_code == 200:
        job = response.json()
        print(f"✓ Job details: {job['title']}")
        return True
    else:
        print("✗ Job details failed:", response.text)
        return False

def test_apply(token, job_id):
    """Test job application"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {"job_id": job_id}
    response = requests.post(f"{BASE_URL}/applications", json=data, headers=headers)
    if response.status_code == 201:
        print("✓ Application submitted")
        return True
    else:
        print("✗ Application failed:", response.text)
        return False

def test_favorites(token, job_id):
    """Test add to favorites"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {"job_id": job_id}
    response = requests.post(f"{BASE_URL}/favorites", json=data, headers=headers)
    if response.status_code == 201:
        print("✓ Added to favorites")
        return True
    else:
        print("✗ Add to favorites failed:", response.text)
        return False

def test_my_applications(token):
    """Test application tracker"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/applications/my-applications", headers=headers)
    if response.status_code == 200:
        apps = response.json()
        print(f"✓ Found {len(apps)} applications")
        return True
    else:
        print("✗ My applications failed:", response.text)
        return False

if __name__ == "__main__":
    print("Testing WorkBridge Job Seeker API")
    print("=" * 40)
    

    token = test_login()
    if not token:
        exit(1)
    

    job_id = test_jobs()
    if not job_id:
        exit(1)
    

    test_job_details(job_id)
    

    test_apply(token, job_id)
    

    test_favorites(token, job_id)
    

    test_my_applications(token)
    
    print("\n✓ All tests completed!")