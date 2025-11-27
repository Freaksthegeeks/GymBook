from config import database
import psycopg2

try:
    # Add the new columns to the clients table if they don't exist
    print("Updating clients table schema...")
    
    # Check if total_paid column exists
    database.cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='clients' AND column_name='total_paid'
    """)
    
    if not database.cur.fetchone():
        print("Adding total_paid column...")
        database.cur.execute("ALTER TABLE clients ADD COLUMN total_paid NUMERIC(10,2) DEFAULT 0")
    
    # Check if balance_due column exists
    database.cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='clients' AND column_name='balance_due'
    """)
    
    if not database.cur.fetchone():
        print("Adding balance_due column...")
        database.cur.execute("ALTER TABLE clients ADD COLUMN balance_due NUMERIC(10,2) DEFAULT 0")
    
    # Commit changes
    database.conn.commit()
    print("Database schema updated successfully!")
    
    # Verify the changes
    print("\nUpdated clients table columns:")
    database.cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'clients' 
        ORDER BY ordinal_position
    """)
    rows = database.cur.fetchall()
    for row in rows:
        print(f"  {row[0]}: {row[1]}")

except Exception as e:
    print(f"Error updating schema: {e}")
    database.conn.rollback()
finally:
    database.conn.close()