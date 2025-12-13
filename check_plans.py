from config import database

try:
    database.cur.execute("SELECT id, planname, days, amount FROM plans")
    rows = database.cur.fetchall()
    print("Existing plans:")
    if rows:
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Days: {row[2]}, Amount: {row[3]}")
    else:
        print("No plans found in the database.")
except Exception as e:
    print(f"Error: {e}")
finally:
    database.conn.close()