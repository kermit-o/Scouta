import requests
import sys
import time
import json
from datetime import datetime

class AppForgeAPITester:
    def __init__(self, base_url="https://appforge-31.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.project_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}")
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout after {timeout}s")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_create_project(self):
        """Test project creation"""
        test_idea = "Quiero crear una aplicación de gestión de tareas que permita a los usuarios crear, editar y eliminar tareas, asignar prioridades y fechas límite, y colaborar con otros usuarios en proyectos compartidos."
        
        success, response = self.run_test(
            "Create Project",
            "POST",
            "projects",
            200,
            data={"user_description": test_idea}
        )
        
        if success and isinstance(response, dict) and 'id' in response:
            self.project_id = response['id']
            print(f"   Project ID: {self.project_id}")
            return True
        return False

    def test_get_project(self):
        """Test getting project by ID"""
        if not self.project_id:
            print("❌ Skipped - No project ID available")
            return False
            
        return self.run_test(
            "Get Project by ID",
            "GET",
            f"projects/{self.project_id}",
            200
        )[0]

    def test_get_all_projects(self):
        """Test getting all projects"""
        return self.run_test(
            "Get All Projects",
            "GET",
            "projects",
            200
        )[0]

    def test_project_progress(self):
        """Test project progress polling"""
        if not self.project_id:
            print("❌ Skipped - No project ID available")
            return False
            
        success, response = self.run_test(
            "Get Project Progress",
            "GET",
            f"projects/{self.project_id}/progress",
            200
        )
        
        if success and isinstance(response, dict):
            progress = response.get('progress', 0)
            status = response.get('status', 'unknown')
            print(f"   Progress: {progress}%, Status: {status}")
            return True
        return False

    def wait_for_project_completion(self, max_wait_time=300):
        """Wait for project to complete processing"""
        if not self.project_id:
            print("❌ No project ID to wait for")
            return False
            
        print(f"\n⏳ Waiting for project {self.project_id} to complete (max {max_wait_time}s)...")
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            success, response = self.run_test(
                "Progress Check",
                "GET", 
                f"projects/{self.project_id}/progress",
                200
            )
            
            if success and isinstance(response, dict):
                progress = response.get('progress', 0)
                status = response.get('status', 'processing')
                current_task = response.get('current_task', 'Unknown')
                
                print(f"   Progress: {progress}% - {current_task}")
                
                if status == 'completed' or progress >= 100:
                    print("✅ Project completed successfully!")
                    return True
                elif status == 'failed':
                    print("❌ Project failed during processing")
                    return False
                    
            time.sleep(5)  # Wait 5 seconds between checks
            
        print(f"❌ Project did not complete within {max_wait_time} seconds")
        return False

    def test_functional_spec(self):
        """Test getting functional specification"""
        if not self.project_id:
            print("❌ Skipped - No project ID available")
            return False
            
        success, response = self.run_test(
            "Get Functional Specification",
            "GET",
            f"projects/{self.project_id}/functional-spec",
            200
        )
        
        if success and isinstance(response, dict):
            user_stories = response.get('user_stories', [])
            criteria = response.get('acceptance_criteria', [])
            print(f"   User stories: {len(user_stories)}, Acceptance criteria: {len(criteria)}")
            return True
        return False

    def test_tech_spec(self):
        """Test getting technical specification"""
        if not self.project_id:
            print("❌ Skipped - No project ID available")
            return False
            
        success, response = self.run_test(
            "Get Technical Specification",
            "GET",
            f"projects/{self.project_id}/tech-spec",
            200
        )
        
        if success and isinstance(response, dict):
            architecture = response.get('architecture', '')
            stack = response.get('recommended_stack', {})
            endpoints = response.get('endpoints', [])
            print(f"   Architecture: {architecture[:50]}...")
            print(f"   Stack components: {len(stack)}, Endpoints: {len(endpoints)}")
            return True
        return False

    def test_project_structure(self):
        """Test getting project structure"""
        if not self.project_id:
            print("❌ Skipped - No project ID available")
            return False
            
        success, response = self.run_test(
            "Get Project Structure",
            "GET",
            f"projects/{self.project_id}/structure",
            200
        )
        
        if success and isinstance(response, dict):
            directory_tree = response.get('directory_tree', {})
            files = response.get('files_to_generate', [])
            print(f"   Directory structure keys: {list(directory_tree.keys())}")
            print(f"   Files to generate: {len(files)}")
            return True
        return False

    def test_generated_code(self):
        """Test getting generated code"""
        if not self.project_id:
            print("❌ Skipped - No project ID available")
            return False
            
        success, response = self.run_test(
            "Get Generated Code",
            "GET",
            f"projects/{self.project_id}/code",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Generated code files: {len(response)}")
            for code_file in response[:3]:  # Show first 3 files
                if isinstance(code_file, dict):
                    file_path = code_file.get('file_path', 'Unknown')
                    file_type = code_file.get('file_type', 'Unknown')
                    print(f"     - {file_path} ({file_type})")
            return True
        return False

def main():
    print("🚀 Starting AppForge API Testing")
    print("=" * 50)
    
    tester = AppForgeAPITester()
    
    # Test sequence
    tests = [
        ("Root Endpoint", tester.test_root_endpoint),
        ("Create Project", tester.test_create_project),
        ("Get Project", tester.test_get_project),
        ("Get All Projects", tester.test_get_all_projects),
        ("Project Progress", tester.test_project_progress),
    ]
    
    # Run basic tests first
    for test_name, test_func in tests:
        test_func()
    
    # Wait for project completion if we have a project
    if tester.project_id:
        project_completed = tester.wait_for_project_completion()
        
        if project_completed:
            # Test specification endpoints
            print("\n📋 Testing Specification Endpoints")
            print("-" * 40)
            tester.test_functional_spec()
            tester.test_tech_spec()
            tester.test_project_structure()
            tester.test_generated_code()
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 FINAL RESULTS")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.project_id:
        print(f"Test Project ID: {tester.project_id}")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())