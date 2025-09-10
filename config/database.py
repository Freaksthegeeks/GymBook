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
    height FLOAT NOT NULL,
    weight FLOAT NOT NULL,
    plan_id INT REFERENCES plans(id) ON DELETE SET NULL,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

            CREATE TABLE IF NOT EXISTS plans (
        id SERIAL PRIMARY KEY,
        planname VARCHAR(50) UNIQUE NOT NULL,
            
        days int NOT NULL,
        amount NUMERIC(10,2)       
    );  
            CREATE TABLE IF NOT EXISTS staffs (
        id SERIAL PRIMARY KEY,
        staffname VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        phonenumber BIGINT NOT NULL,
        role VARCHAR(50) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP       
    );  

            CREATE TABLE IF NOT EXISTS leads (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        phonenumber BIGINT NOT NULL,
        notes TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
         CREATE TABLE IF NOT EXISTS loggingcredentials (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL,
        password VARCHAR(100) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
        -- Stores all payments made by clients
CREATE TABLE IF NOT EXISTS payments (
  id SERIAL PRIMARY KEY,
  client_id INT NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  amount NUMERIC(12,2) NOT NULL,
  paid_at TIMESTAMP NOT NULL,
  note TEXT,
  method VARCHAR(32),
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Keeps running balance (optional but helpful for quick lookup)
CREATE TABLE IF NOT EXISTS client_balance (
    client_id INT PRIMARY KEY REFERENCES clients(id) ON DELETE CASCADE,
    total_paid NUMERIC(10,2) DEFAULT 0,
    total_due NUMERIC(10,2) DEFAULT 0,
    last_payment DATE
);

""")
conn.commit()
