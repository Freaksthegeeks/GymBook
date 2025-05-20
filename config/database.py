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
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
""")
conn.commit()
