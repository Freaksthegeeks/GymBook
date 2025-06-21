import psycopg2
import psycopg2.extras


# Database connection
conn = psycopg2.connect(
    dbname="gym",
    user="skvar",
    password="Root1234",
    host="localhost",
    port="5432"
)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

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
        
    );
            CREATE TABLE IF NOT EXISTS plans (
        id SERIAL PRIMARY KEY,
        planname VARCHAR(50) UNIQUE NOT NULL,
        days int NOT NULL,
        amount NUMERIC(10,2)       
    );           
""")
conn.commit()
