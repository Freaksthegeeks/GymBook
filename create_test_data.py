import requests
import json
from datetime import date, timedelta

# Base URL for the API
BASE_URL = "http://localhost:8000"

# Get auth token
def get_auth_token():
    login_data = {
        "email": "admin@gym.com",
        "password": "admin123"
    }
    
    response = requests.post(
        f"{BASE_URL}/login/",
        headers={"Content-Type": "application/json"},
        data=json.dumps(login_data)
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception("Failed to authenticate")

# Create test clients
def create_test_clients(token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # Create a plan first if needed
    plans_response = requests.get(f"{BASE_URL}/plans/", headers=headers)
    plans = plans_response.json()["plans"]
    
    if not plans:
        # Create a test plan
        plan_data = {
            "planname": "Test Plan",
            "days": 30,
            "amount": 50.0
        }
        
        response = requests.post(
            f"{BASE_URL}/plans/",
            headers=headers,
            data=json.dumps(plan_data)
        )
        
        if response.status_code == 200:
            plan_id = response.json()["id"]
        else:
            raise Exception("Failed to create plan")
    else:
        plan_id = plans[0]["id"]
    
    # Create test clients with different expiration dates
    test_clients = [
        {
            "clientname": "Active Client 1",
            "phonenumber": "1111111111",
            "dateofbirth": "1990-01-01",
            "gender": "Male",
            "bloodgroup": "O+",
            "address": "Test Address 1",
            "notes": "Active client",
            "email": "active1@example.com",
            "height": 175.0,
            "weight": 70.0,
            "plan_id": plan_id,
            "start_date": str(date.today())
        },
        {
            "clientname": "Active Client 2",
            "phonenumber": "2222222222",
            "dateofbirth": "1992-02-02",
            "gender": "Female",
            "bloodgroup": "A+",
            "address": "Test Address 2",
            "notes": "Active client",
            "email": "active2@example.com",
            "height": 165.0,
            "weight": 60.0,
            "plan_id": plan_id,
            "start_date": str(date.today())
        },
        {
            "clientname": "Expiring Client",
            "phonenumber": "3333333333",
            "dateofbirth": "1985-03-03",
            "gender": "Male",
            "bloodgroup": "B+",
            "address": "Test Address 3",
            "notes": "Expiring soon",
            "email": "expiring@example.com",
            "height": 180.0,
            "weight": 75.0,
            "plan_id": plan_id,
            "start_date": str(date.today() - timedelta(days=25))  # 5 days left
        },
        {
            "clientname": "Expired Client",
            "phonenumber": "4444444444",
            "dateofbirth": "1988-04-04",
            "gender": "Female",
            "bloodgroup": "AB+",
            "address": "Test Address 4",
            "notes": "Expired recently",
            "email": "expired@example.com",
            "height": 170.0,
            "weight": 65.0,
            "plan_id": plan_id,
            "start_date": str(date.today() - timedelta(days=45))  # Expired 15 days ago
        }
    ]
    
    for client_data in test_clients:
        response = requests.post(
            f"{BASE_URL}/clients/",
            headers=headers,
            data=json.dumps(client_data)
        )
        
        if response.status_code == 200:
            print(f"Created client: {client_data['clientname']}")
        else:
            print(f"Failed to create client {client_data['clientname']}: {response.json()}")

if __name__ == "__main__":
    try:
        token = get_auth_token()
        print("Authentication successful")
        create_test_clients(token)
        print("Test data creation completed")
    except Exception as e:
        print(f"Error: {e}")