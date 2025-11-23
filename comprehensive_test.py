import requests
import json
from datetime import date

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_clients_crud():
    """Test all CRUD operations for clients"""
    print("=== Testing Clients CRUD Operations ===")
    
    # 1. Get all clients (should be empty or have existing ones)
    print("\n1. Getting all clients...")
    response = requests.get(f"{BASE_URL}/clients/")
    print(f"Status: {response.status_code}")
    clients = response.json()["clients"]
    print(f"Found {len(clients)} clients")
    
    # 2. Create a new client
    print("\n2. Creating a new client...")
    new_client = {
        "clientname": "John Doe Test",
        "phonenumber": "9876543210",
        "dateofbirth": "1985-05-15",
        "gender": "Male",
        "bloodgroup": "B+",
        "address": "123 Test Street",
        "notes": "Test client for CRUD operations",
        "email": "johndoetest@example.com",
        "height": 180.0,
        "weight": 75.5,
        "plan_id": 24,  # Using existing plan
        "start_date": str(date.today())
    }
    
    response = requests.post(
        f"{BASE_URL}/clients/",
        headers={"Content-Type": "application/json"},
        data=json.dumps(new_client)
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        client_data = response.json()
        client_id = client_data["id"]
        print(f"Created client with ID: {client_id}")
    else:
        print(f"Error: {response.json()}")
        return
    
    # 3. Get all clients again (should have one more)
    print("\n3. Getting all clients after creation...")
    response = requests.get(f"{BASE_URL}/clients/")
    print(f"Status: {response.status_code}")
    clients = response.json()["clients"]
    print(f"Found {len(clients)} clients")
    
    # 4. Get the specific client we just created
    print("\n4. Getting the specific client...")
    response = requests.get(f"{BASE_URL}/clients/{client_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        client_details = response.json()
        print(f"Client details: {client_details}")
    else:
        print(f"Error: {response.json()}")
    
    # 5. Delete the client
    print("\n5. Deleting the client...")
    response = requests.delete(f"{BASE_URL}/clients/{client_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Client deleted successfully")
    else:
        print(f"Error: {response.json()}")
    
    # 6. Verify client is deleted
    print("\n6. Verifying client is deleted...")
    response = requests.get(f"{BASE_URL}/clients/")
    print(f"Status: {response.status_code}")
    clients = response.json()["clients"]
    print(f"Found {len(clients)} clients after deletion")

def test_plans_crud():
    """Test all CRUD operations for plans"""
    print("\n\n=== Testing Plans CRUD Operations ===")
    
    # 1. Get all plans
    print("\n1. Getting all plans...")
    response = requests.get(f"{BASE_URL}/plans/")
    print(f"Status: {response.status_code}")
    plans = response.json()["plans"]
    print(f"Found {len(plans)} plans")
    original_plan_count = len(plans)
    
    # 2. Create a new plan
    print("\n2. Creating a new plan...")
    new_plan = {
        "planname": f"Test Plan {date.today().strftime('%Y%m%d%H%M%S')}",  # Unique name
        "days": 45,
        "amount": 75.0
    }
    
    response = requests.post(
        f"{BASE_URL}/plans/",
        headers={"Content-Type": "application/json"},
        data=json.dumps(new_plan)
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        plan_data = response.json()
        plan_id = plan_data["id"]
        print(f"Created plan with ID: {plan_id}")
    else:
        print(f"Error: {response.json()}")
        return
    
    # 3. Get all plans again (should have one more)
    print("\n3. Getting all plans after creation...")
    response = requests.get(f"{BASE_URL}/plans/")
    print(f"Status: {response.status_code}")
    plans = response.json()["plans"]
    print(f"Found {len(plans)} plans")
    
    # 4. Delete the plan
    print("\n4. Deleting the plan...")
    response = requests.delete(f"{BASE_URL}/plans/{plan_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Plan deleted successfully")
    else:
        print(f"Error: {response.json()}")
    
    # 5. Verify plan is deleted
    print("\n5. Verifying plan is deleted...")
    response = requests.get(f"{BASE_URL}/plans/")
    print(f"Status: {response.status_code}")
    plans = response.json()["plans"]
    print(f"Found {len(plans)} plans after deletion")
    print(f"Expected: {original_plan_count}, Actual: {len(plans)}")

def test_staff_crud():
    """Test all CRUD operations for staff"""
    print("\n\n=== Testing Staff CRUD Operations ===")
    
    # 1. Get all staff
    print("\n1. Getting all staff...")
    response = requests.get(f"{BASE_URL}/staffs/")
    print(f"Status: {response.status_code}")
    staffs = response.json()["staffs"]
    print(f"Found {len(staffs)} staff members")
    original_staff_count = len(staffs)
    
    # 2. Create a new staff member
    print("\n2. Creating a new staff member...")
    new_staff = {
        "staffname": f"Test Staff {date.today().strftime('%Y%m%d%H%M%S')}",  # Unique name
        "email": "teststaff@example.com",
        "phonenumber": 1234567890,
        "role": "Trainer"
    }
    
    response = requests.post(
        f"{BASE_URL}/staffs/",
        headers={"Content-Type": "application/json"},
        data=json.dumps(new_staff)
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        staff_data = response.json()
        staff_id = staff_data["id"]
        print(f"Created staff with ID: {staff_id}")
    else:
        print(f"Error: {response.json()}")
        return
    
    # 3. Get all staff again (should have one more)
    print("\n3. Getting all staff after creation...")
    response = requests.get(f"{BASE_URL}/staffs/")
    print(f"Status: {response.status_code}")
    staffs = response.json()["staffs"]
    print(f"Found {len(staffs)} staff members")
    
    # 4. Delete the staff member
    print("\n4. Deleting the staff member...")
    response = requests.delete(f"{BASE_URL}/staffs/{staff_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Staff member deleted successfully")
    else:
        print(f"Error: {response.json()}")
    
    # 5. Verify staff member is deleted
    print("\n5. Verifying staff member is deleted...")
    response = requests.get(f"{BASE_URL}/staffs/")
    print(f"Status: {response.status_code}")
    staffs = response.json()["staffs"]
    print(f"Found {len(staffs)} staff members after deletion")
    print(f"Expected: {original_staff_count}, Actual: {len(staffs)}")

if __name__ == "__main__":
    print("Starting comprehensive API tests...")
    test_clients_crud()
    test_plans_crud()
    test_staff_crud()
    print("\n=== All tests completed ===")