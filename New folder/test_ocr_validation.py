import os
import time
import requests
import threading
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:10000"  # Update if your server runs on a different port
TEST_IMAGE_PATH = "test_document.jpg"  # Path to a test document
RESULTS_FILE = "test_results.txt"

# Test data
test_cases = [
    {
        "name": "Valid Student Document",
        "file": TEST_IMAGE_PATH,
        "last_name": "Doe",
        "birthday": "1990-01-15",
        "student_id": "S12345678",
        "expected_verified": True
    },
    {
        "name": "Invalid Student ID",
        "file": TEST_IMAGE_PATH,
        "last_name": "Doe",
        "birthday": "1990-01-15",
        "student_id": "INVALID_ID",
        "expected_verified": False
    }
]

def log_result(test_name, result, response_time=None):
    """Log test results to console and file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(RESULTS_FILE, "a") as f:
        if response_time is not None:
            log_line = f"[{timestamp}] {test_name}: {result} (Response Time: {response_time:.2f}s)\n"
        else:
            log_line = f"[{timestamp}] {test_name}: {result}\n"
        f.write(log_line)
    print(log_line.strip())

def test_single_verification():
    """Test a single verification request"""
    test_case = test_cases[0]
    start_time = time.time()
    
    try:
        with open(test_case["file"], 'rb') as f:
            files = {'file': f}
            data = {
                'last_name': test_case["last_name"],
                'birthday': test_case["birthday"],
                'student_id': test_case["student_id"]
            }
            
            # Submit verification request
            response = requests.post(f"{BASE_URL}/api/verify_student", files=files, data=data)
            response.raise_for_status()
            
            # Get task ID and poll for result
            task_id = response.json()['task_id']
            result = poll_verification_result(task_id)
            
            response_time = time.time() - start_time
            
            if result.get('success') and result.get('verified') == test_case["expected_verified"]:
                log_result("Unit Test - Single Verification", "PASSED", response_time)
                return True, response_time
            else:
                log_result("Unit Test - Single Verification", f"FAILED - Unexpected result: {result}", response_time)
                return False, response_time
                
    except Exception as e:
        response_time = time.time() - start_time
        log_result("Unit Test - Single Verification", f"ERROR - {str(e)}", response_time)
        return False, response_time

def poll_verification_result(task_id, max_attempts=10, delay=1):
    """Poll for verification result with retry logic"""
    for _ in range(max_attempts):
        response = requests.get(f"{BASE_URL}/api/verify_status/{task_id}")
        data = response.json()
        
        if data['status'] == 'completed':
            return data['result']
        elif data['status'] == 'error':
            raise Exception(f"Verification failed: {data.get('error', 'Unknown error')}")
            
        time.sleep(delay)
    
    raise Exception("Max polling attempts reached")

def run_stress_test(num_requests=20, max_workers=5):
    """Run multiple verification requests in parallel to test system under load"""
    test_case = test_cases[0]  # Use the valid test case
    results = []
    
    def make_request(_):
        try:
            start_time = time.time()
            with open(test_case["file"], 'rb') as f:
                files = {'file': f}
                data = {
                    'last_name': test_case["last_name"],
                    'birthday': test_case["birthday"],
                    'student_id': test_case["student_id"]
                }
                
                # Submit verification request
                response = requests.post(
                    f"{BASE_URL}/api/verify_student",
                    files=files,
                    data=data,
                    timeout=30
                )
                response.raise_for_status()
                
                # Get task ID and poll for result
                task_id = response.json()['task_id']
                result = poll_verification_result(task_id)
                
                response_time = time.time() - start_time
                return {
                    'success': True,
                    'time': response_time,
                    'verified': result.get('verified', False)
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'time': time.time() - start_time if 'start_time' in locals() else 0
            }
    
    # Run stress test
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(make_request, range(num_requests)))
    
    total_time = time.time() - start_time
    
    # Calculate statistics
    successful = sum(1 for r in results if r.get('success', False))
    failed = num_requests - successful
    times = [r['time'] for r in results if 'time' in r]
    avg_time = sum(times) / len(times) if times else 0
    
    # Log results
    log_result("\n=== STRESS TEST RESULTS ===", "")
    log_result("Total Requests", f"{num_requests}")
    log_result("Successful", f"{successful}")
    log_result("Failed", f"{failed}")
    log_result("Total Time", f"{total_time:.2f} seconds")
    log_result("Average Response Time", f"{avg_time:.2f} seconds")
    log_result("Requests Per Second", f"{num_requests / total_time:.2f}")
    
    return {
        'total_requests': num_requests,
        'successful': successful,
        'failed': failed,
        'total_time': total_time,
        'avg_response_time': avg_time,
        'requests_per_second': num_requests / total_time if total_time > 0 else 0
    }

if __name__ == "__main__":
    # Clear previous results
    if os.path.exists(RESULTS_FILE):
        os.remove(RESULTS_FILE)
    
    print("=== Starting OCR Validation Tests ===\n")
    
    # Run unit tests
    print("Running unit tests...")
    unit_test_passed, unit_test_time = test_single_verification()
    
    # Run stress test if unit test passed
    if unit_test_passed:
        print("\nRunning stress test...")
        stress_test_results = run_stress_test(num_requests=20, max_workers=5)
    
    print("\n=== Test Complete ===")
    print(f"Results saved to: {os.path.abspath(RESULTS_FILE)}")
