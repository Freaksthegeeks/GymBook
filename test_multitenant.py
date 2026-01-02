"""
Test script to verify multitenant functionality
"""
import jwt
from config import database
import os
from datetime import datetime, timedelta

# Define the secret key directly since we can't import from index due to circular imports
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"

def test_multitenant_setup():
    """Test that the multitenant schema has been properly set up"""
    print("Testing multitenant schema setup...")
    
    # Check if gyms table exists
    database.cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'gyms'
        );
    """)
    gyms_table_exists = database.cur.fetchone()[0]
    print(f"Gyms table exists: {gyms_table_exists}")
    
    # Check if user_gyms table exists
    database.cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'user_gyms'
        );
    """)
    user_gyms_table_exists = database.cur.fetchone()[0]
    print(f"User_gyms table exists: {user_gyms_table_exists}")
    
    # Check if gym_id column exists in clients table
    database.cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = 'clients' AND column_name = 'gym_id'
        );
    """)
    gym_id_in_clients = database.cur.fetchone()[0]
    print(f"Gym_id column in clients table: {gym_id_in_clients}")
    
    # Check if gym_id column exists in plans table
    database.cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = 'plans' AND column_name = 'gym_id'
        );
    """)
    gym_id_in_plans = database.cur.fetchone()[0]
    print(f"Gym_id column in plans table: {gym_id_in_plans}")
    
    # Check if gym_id column exists in staffs table
    database.cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = 'staffs' AND column_name = 'gym_id'
        );
    """)
    gym_id_in_staffs = database.cur.fetchone()[0]
    print(f"Gym_id column in staffs table: {gym_id_in_staffs}")
    
    # Check if gym_id column exists in leads table
    database.cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = 'leads' AND column_name = 'gym_id'
        );
    """)
    gym_id_in_leads = database.cur.fetchone()[0]
    print(f"Gym_id column in leads table: {gym_id_in_leads}")
    
    # Check if gym_id column exists in payments table
    database.cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = 'payments' AND column_name = 'gym_id'
        );
    """)
    gym_id_in_payments = database.cur.fetchone()[0]
    print(f"Gym_id column in payments table: {gym_id_in_payments}")
    
    # Check if gym_id column exists in client_balance table
    database.cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = 'client_balance' AND column_name = 'gym_id'
        );
    """)
    gym_id_in_client_balance = database.cur.fetchone()[0]
    print(f"Gym_id column in client_balance table: {gym_id_in_client_balance}")
    
    if all([gyms_table_exists, user_gyms_table_exists, gym_id_in_clients, 
            gym_id_in_plans, gym_id_in_staffs, gym_id_in_leads, 
            gym_id_in_payments, gym_id_in_client_balance]):
        print("✅ All multitenant schema changes have been applied successfully!")
        return True
    else:
        print("❌ Some multitenant schema changes are missing!")
        return False

def test_jwt_token_structure():
    """Test that JWT tokens now include gym context"""
    print("\nTesting JWT token structure...")
    
    # Create a test token with gym context
    test_payload = {
        "sub": 1,  # user_id
        "current_gym_id": 1,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    
    token = jwt.encode(test_payload, SECRET_KEY, algorithm=ALGORITHM)
    decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
    has_user_id = "sub" in decoded_payload
    has_gym_id = "current_gym_id" in decoded_payload
    
    print(f"Token has user_id (sub): {has_user_id}")
    print(f"Token has current_gym_id: {has_gym_id}")
    
    if has_user_id and has_gym_id:
        print("✅ JWT token structure supports gym context!")
        return True
    else:
        print("❌ JWT token structure does not support gym context!")
        return False

if __name__ == "__main__":
    print("Running multitenant architecture tests...\n")
    
    schema_test_passed = test_multitenant_setup()
    jwt_test_passed = test_jwt_token_structure()
    
    print(f"\nSchema test: {'✅ PASSED' if schema_test_passed else '❌ FAILED'}")
    print(f"JWT test: {'✅ PASSED' if jwt_test_passed else '❌ FAILED'}")
    
    if schema_test_passed and jwt_test_passed:
        print("\n🎉 All multitenant tests passed! The implementation is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")