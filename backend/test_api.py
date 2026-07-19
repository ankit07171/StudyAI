"""
Simple API testing script
Run this after starting the server to verify everything works
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}→ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}! {message}{Colors.END}")

# Store token for authenticated requests
access_token = None

def test_health_check():
    """Test health check endpoint"""
    print_info("Testing health check...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print_success("Health check passed")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server. Is it running?")
        return False

def test_register():
    """Test user registration"""
    print_info("Testing user registration...")
    global access_token
    
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        
        if response.status_code == 201:
            result = response.json()
            access_token = result['access_token']
            print_success(f"Registration successful. User ID: {result['user']['id']}")
            return True
        elif response.status_code == 400:
            # User might already exist, try login
            print_warning("User already exists, trying login...")
            return test_login()
        else:
            print_error(f"Registration failed: {response.text}")
            return False
    except Exception as e:
        print_error(f"Registration error: {e}")
        return False

def test_login():
    """Test user login"""
    print_info("Testing user login...")
    global access_token
    
    data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=data)
        
        if response.status_code == 200:
            result = response.json()
            access_token = result['access_token']
            print_success("Login successful")
            return True
        else:
            print_error(f"Login failed: {response.text}")
            return False
    except Exception as e:
        print_error(f"Login error: {e}")
        return False

def test_create_subject():
    """Test subject creation"""
    print_info("Testing subject creation...")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "name": "Operating System",
        "code": "CS301",
        "semester": "Semester 5",
        "description": "OS fundamentals and concepts"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/subjects", json=data, headers=headers)
        
        if response.status_code == 201:
            result = response.json()
            print_success(f"Subject created. ID: {result['id']}")
            return result['id']
        else:
            print_error(f"Subject creation failed: {response.text}")
            return None
    except Exception as e:
        print_error(f"Subject creation error: {e}")
        return None

def test_get_subjects():
    """Test getting all subjects"""
    print_info("Testing get subjects...")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/subjects", headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Retrieved {len(result)} subject(s)")
            return True
        else:
            print_error(f"Get subjects failed: {response.text}")
            return False
    except Exception as e:
        print_error(f"Get subjects error: {e}")
        return False

def test_user_profile():
    """Test getting user profile"""
    print_info("Testing get user profile...")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Profile retrieved: {result['email']}")
            return True
        else:
            print_error(f"Get profile failed: {response.text}")
            return False
    except Exception as e:
        print_error(f"Get profile error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("AI Study Assistant - API Test Suite")
    print("=" * 60)
    print()
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Health Check
    tests_total += 1
    if test_health_check():
        tests_passed += 1
    print()
    
    # Test 2: Registration
    tests_total += 1
    if test_register():
        tests_passed += 1
    print()
    
    # Test 3: User Profile
    if access_token:
        tests_total += 1
        if test_user_profile():
            tests_passed += 1
        print()
        
        # Test 4: Create Subject
        tests_total += 1
        subject_id = test_create_subject()
        if subject_id:
            tests_passed += 1
        print()
        
        # Test 5: Get Subjects
        tests_total += 1
        if test_get_subjects():
            tests_passed += 1
        print()
    
    # Summary
    print("=" * 60)
    print(f"Tests Passed: {tests_passed}/{tests_total}")
    print("=" * 60)
    
    if tests_passed == tests_total:
        print_success("All tests passed! API is working correctly.")
    else:
        print_warning(f"{tests_total - tests_passed} test(s) failed.")
        print_info("Check the server logs for more details.")
    
    print()
    print("Next steps:")
    print("1. Try uploading a PDF using the /upload endpoint")
    print("2. Ask questions using the /chat endpoint")
    print("3. Generate notes using the /notes endpoint")
    print()
    print("Full API documentation: http://localhost:8000/api/docs")

if __name__ == "__main__":
    main()
