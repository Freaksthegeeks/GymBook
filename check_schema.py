from config import database

# Check clients table schema
print("Clients table columns:")
database.cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'clients' 
    ORDER BY ordinal_position
""")
rows = database.cur.fetchall()
for row in rows:
    print(f"  {row[0]}: {row[1]}")

print("\nPlans table columns:")
database.cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'plans' 
    ORDER BY ordinal_position
""")
rows = database.cur.fetchall()
for row in rows:
    print(f"  {row[0]}: {row[1]}")

# Close connection
database.conn.close()