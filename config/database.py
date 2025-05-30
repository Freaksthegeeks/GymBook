import psycopg2

# Database connection
conn = psycopg2.connect(
    dbname="gym",
    user="skvar",
    password="Root1234",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Ensure the table exists
cur.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id SERIAL PRIMARY KEY,
        clientname VARCHAR(100) UNIQUE NOT NULL,
        phonenumber BIGINT NOT NULL,
        dateofbirth DATE NOT NULL,
        gender VARCHAR(10) NOT NULL,
        bloodgroup VARCHAR(5) NOT NULL,
        address TEXT NOT NULL,
        notes TEXT,     
        email VARCHAR(100) UNIQUE NOT NULL,
        height Float NOT NULL,
        weight Float NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        
    )
""")
conn.commit()
