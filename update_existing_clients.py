from config import database

try:
    # Update existing clients to set correct initial values for payment tracking
    print("Updating existing clients payment tracking fields...")
    
    # Set balance_due to plan amount and total_paid to 0 for all existing clients
    database.cur.execute("""
        UPDATE clients 
        SET total_paid = 0, 
            balance_due = COALESCE(
                (SELECT amount FROM plans WHERE plans.id = clients.plan_id), 
                0
            )
    """)
    
    # Commit changes
    database.conn.commit()
    print("Existing clients updated successfully!")
    
except Exception as e:
    print(f"Error updating clients: {e}")
    database.conn.rollback()
finally:
    database.conn.close()