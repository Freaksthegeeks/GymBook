import psycopg2
import psycopg2.extras
import psycopg2.errors


# Database connection
conn = psycopg2.connect(
    dbname="gym",
    user="skvar",
    password="Root1234",
    host="localhost",
    port="5432"
)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# Ensure the tables exist in the correct order (referenced tables first)

# Create plans table first (referenced by clients table)
cur.execute("""
    CREATE TABLE IF NOT EXISTS plans (
        id SERIAL PRIMARY KEY,
        planname VARCHAR(50) UNIQUE NOT NULL,
        days int NOT NULL,
        amount NUMERIC(10,2)       
    );  
""")

# Create other tables that don't have dependencies
cur.execute("""
    CREATE TABLE IF NOT EXISTS staffs (
        id SERIAL PRIMARY KEY,
        staffname VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        phonenumber BIGINT NOT NULL,
        role VARCHAR(50) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP       
    );  
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        phonenumber BIGINT NOT NULL,
        notes TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS loggingcredentials (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL,
        password VARCHAR(100) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
""")

# Create clients table (references plans table)
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    total_paid NUMERIC(10,2) DEFAULT 0,
    balance_due NUMERIC(10,2) DEFAULT 0
);
""")

# Create payments table (references clients table)
cur.execute("""
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
""")

# Create client_balance table (references clients table)
cur.execute("""
-- Keeps running balance (optional but helpful for quick lookup)
CREATE TABLE IF NOT EXISTS client_balance (
    client_id INT PRIMARY KEY REFERENCES clients(id) ON DELETE CASCADE,
    gym_id INT REFERENCES gyms(id) ON DELETE CASCADE,
    total_paid NUMERIC(10,2) DEFAULT 0,
    total_due NUMERIC(10,2) DEFAULT 0,
    last_payment DATE
);
""")
# Create gyms table
cur.execute("""
    CREATE TABLE IF NOT EXISTS gyms (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        address TEXT,
        phone VARCHAR(20),
        email VARCHAR(100),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
""")

# Create user_gyms table to manage the many-to-many relationship between users and gyms
cur.execute("""
    CREATE TABLE IF NOT EXISTS user_gyms (
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL REFERENCES loggingcredentials(id) ON DELETE CASCADE,
        gym_id INT NOT NULL REFERENCES gyms(id) ON DELETE CASCADE,
        role VARCHAR(50) DEFAULT 'member',
        is_owner BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, gym_id)
    );
""")

# Add gym_id column to existing tables that need to be associated with a gym

# Add gym_id to plans table
try:
    cur.execute("ALTER TABLE plans ADD COLUMN gym_id INT REFERENCES gyms(id) ON DELETE CASCADE;")
except psycopg2.errors.DuplicateColumn:
    conn.rollback()  # Rollback the failed ALTER TABLE command
    pass  # Column already exists, continue

# Add gym_id to staffs table
try:
    cur.execute("ALTER TABLE staffs ADD COLUMN gym_id INT REFERENCES gyms(id) ON DELETE CASCADE;")
except psycopg2.errors.DuplicateColumn:
    conn.rollback()  # Rollback the failed ALTER TABLE command
    pass  # Column already exists, continue

# Add gym_id to leads table
try:
    cur.execute("ALTER TABLE leads ADD COLUMN gym_id INT REFERENCES gyms(id) ON DELETE CASCADE;")
except psycopg2.errors.DuplicateColumn:
    conn.rollback()  # Rollback the failed ALTER TABLE command
    pass  # Column already exists, continue

# Add gym_id to clients table
try:
    cur.execute("ALTER TABLE clients ADD COLUMN gym_id INT REFERENCES gyms(id) ON DELETE CASCADE;")
except psycopg2.errors.DuplicateColumn:
    conn.rollback()  # Rollback the failed ALTER TABLE command
    pass  # Column already exists, continue

# Add gym_id to payments table
try:
    cur.execute("ALTER TABLE payments ADD COLUMN gym_id INT REFERENCES gyms(id) ON DELETE CASCADE;")
except psycopg2.errors.DuplicateColumn:
    conn.rollback()  # Rollback the failed ALTER TABLE command
    pass  # Column already exists, continue

conn.commit()


def initialize_multitenant_for_existing_users():
    """
    Initialize multitenant architecture for existing users by:
    1. Creating a default gym for each user
    2. Adding the user to their default gym as owner
    3. Assigning existing data to their respective gyms
    """
    try:
        # Get all existing users
        cur.execute("SELECT id, username FROM loggingcredentials")
        users = cur.fetchall()
        
        for user in users:
            user_id = user[0]
            username = user[1]
            
            # Create a default gym for the user
            gym_name = f"{username}'s Gym"
            cur.execute("""
                INSERT INTO gyms (name, description)
                VALUES (%s, %s)
                RETURNING id
            """, (gym_name, f"Default gym for {username}"))
            
            gym_id = cur.fetchone()[0]
            
            # Add user to their default gym as owner
            cur.execute("""
                INSERT INTO user_gyms (user_id, gym_id, role, is_owner)
                VALUES (%s, %s, %s, %s)
            """, (user_id, gym_id, 'admin', True))
            
            # Assign existing data to this gym
            # Update plans
            cur.execute("UPDATE plans SET gym_id = %s WHERE gym_id IS NULL", (gym_id,))
            # Update staffs
            cur.execute("UPDATE staffs SET gym_id = %s WHERE gym_id IS NULL", (gym_id,))
            # Update leads
            cur.execute("UPDATE leads SET gym_id = %s WHERE gym_id IS NULL", (gym_id,))
            # Update clients
            cur.execute("UPDATE clients SET gym_id = %s WHERE gym_id IS NULL", (gym_id,))
            # Update payments
            cur.execute("UPDATE payments SET gym_id = %s WHERE gym_id IS NULL", (gym_id,))
            # Update client_balance
            cur.execute("UPDATE client_balance SET gym_id = %s WHERE gym_id IS NULL", (gym_id,))
        
        conn.commit()
        print(f"Initialized multitenant architecture for {len(users)} existing users")
        
    except Exception as e:
        conn.rollback()
        print(f"Error initializing multitenant architecture: {str(e)}")
        raise

# Initialize multitenant architecture for existing users if needed
# initialize_multitenant_for_existing_users()