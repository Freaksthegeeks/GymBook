import requests

# Test the dashboard statistics endpoint
def test_dashboard():
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjgsInVzZXJuYW1lIjoiYWRtaW4iLCJleHAiOjE3NjM1NTczOTR9.3zJ9NARmGYzqLoWfd2hmLJYXHEa-PkSAopXobQm6aOU'
    
    try:
        response = requests.get(
            'http://localhost:8000/dashboard/stats',
            headers={'Authorization': f'Bearer {token}'}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_dashboard()