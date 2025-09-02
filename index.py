from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from config import database  # Import database connection
from datetime import date, timedelta, datetime
from fastapi import Query
from typing import Optional
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# JWT Configuration
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security
security = HTTPBearer()

# Authentication Models
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str

# ✅ client Model (Request Body)
class client(BaseModel):
    clientname: str
    phonenumber: str
    dateofbirth: str
    gender: str
    bloodgroup: str
    address: str
    notes: Optional[str] = None
    email: str
    height: float
    weight: float
    plan_id:int
    start_date: date=date.today()

# Authentication Utility Functions
def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Authentication Endpoints
@app.post("/register/", response_model=dict)
def register_user(user: UserRegister):
    """Register a new user"""
    try:
        # Check if email already exists
        database.cur.execute("SELECT id FROM loggingcredentials WHERE email = %s", (user.email,))
        if database.cur.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Check if username already exists
        database.cur.execute("SELECT id FROM loggingcredentials WHERE username = %s", (user.username,))
        if database.cur.fetchone():
            raise HTTPException(status_code=400, detail="Username already taken")
        
        # Hash password and insert user
        hashed_password = hash_password(user.password)
        database.cur.execute("""
            INSERT INTO loggingcredentials (username, email, password)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (user.username, user.email, hashed_password))
        
        user_id = database.cur.fetchone()[0]
        database.conn.commit()
        
        return {"message": "User registered successfully", "user_id": user_id}
        
    except HTTPException:
        raise
    except Exception as e:
        database.conn.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/login/", response_model=Token)
def login_user(user: UserLogin):
    """Login user and return JWT token"""
    try:
        # Find user by email
        database.cur.execute("""
            SELECT id, username, password FROM loggingcredentials 
            WHERE email = %s
        """, (user.email,))
        
        user_data = database.cur.fetchone()
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        user_id, username, hashed_password = user_data
        
        # Verify password
        if not verify_password(user.password, hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_id, "username": username},
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user_id,
            username=username
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.get("/me/", response_model=dict)
def get_current_user_info(current_user_id: int = Depends(get_current_user)):
    """Get current user information"""
    try:
        database.cur.execute("""
            SELECT id, username, email, created_at FROM loggingcredentials 
            WHERE id = %s
        """, (current_user_id,))
        
        user_data = database.cur.fetchone()
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": user_data[0],
            "username": user_data[1],
            "email": user_data[2],
            "created_at": str(user_data[3])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user info: {str(e)}")

#CLIENTS

# ✅ Create client (add client page)
@app.post("/clients/")
def create_client(client: client):
    try:
        # 1) Fetch plan duration from plans table
        database.cur.execute("SELECT days FROM plans WHERE id = %s", (client.plan_id,))
        plan = database.cur.fetchone()
        if not plan:
            raise HTTPException(status_code=400, detail="Invalid plan ID")

        duration = plan[0]  # 'days' column
        end_date = client.start_date + timedelta(days=duration)

        # 2) Insert into clients with plan_id, start_date, end_date
        database.cur.execute("""
            INSERT INTO clients
                (clientname, phonenumber, dateofbirth, gender, bloodgroup,
                 address, notes, email, height, weight,
                 plan_id, start_date, end_date)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id
        """, (
            client.clientname, client.phonenumber, client.dateofbirth,
            client.gender, client.bloodgroup, client.address, client.notes,
            client.email, client.height, client.weight,
            client.plan_id, client.start_date, end_date
        ))
        database.conn.commit()
        client_id = database.cur.fetchone()[0]
        return {"id": client_id, "end_date": str(end_date), "message": "Client created successfully"}

    except Exception as e:
        database.conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
# ✅ Read All clients(total members)
@app.get("/clients/")
def get_clients():
    database.cur.execute("""
        SELECT c.id, c.clientname, c.phonenumber, c.dateofbirth, c.gender, c.bloodgroup,
               c.address, c.notes, c.email, c.height, c.weight,
               c.start_date, c.end_date,
               p.planname, p.days, p.amount
        FROM clients c
        JOIN plans p ON c.plan_id = p.id
    """)
    rows = database.cur.fetchall()
    clients = []
    for row in rows:
        clients.append({
            "id": row[0],
            "clientname": row[1],
            "phonenumber": str(row[2]),
            "dateofbirth": str(row[3]),
            "gender": row[4],
            "bloodgroup": row[5],
            "address": row[6],
            "notes": row[7],
            "email": row[8],
            "height": float(row[9]),
            "weight": float(row[10]),
            "start_date": str(row[11]),
            "end_date": str(row[12]) if row[12] else None,
            "planname": row[13],
            "days": row[14],
            "amount": float(row[15]) if row[15] else None,
        })
    return {"clients": clients}

# ✅ Read Single client(use it as search function)
@app.get("/clients/{client_id}")
def get_client(client_id: int):
    database.cur.execute("SELECT id,clientname,phonenumber,dateofbirth,gender,bloodgroup,address,notes,email,height,weight FROM clients WHERE id = %s", (client_id,))
    row = database.cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="client not found")
    client = {
        "id": row[0],
        "clientname": row[1],
        "phonenumber": str(row[2]),
        "dateofbirth": str(row[3]),
        "gender": row[4],
        "bloodgroup": row[5],
        "address": row[6],
        "notes": row[7],
        "email": row[8],
        "height": float(row[9]),
        "weight": float(row[10]),
    }
    return {"specific client detail": client}  

# ✅ Update client(updating create page details we can add it in edit option)
@app.put("/clients/{client_id}")
def update_client(client_id: int, client: client):
   # Fetch plan duration
    database.cur.execute("SELECT days FROM plans WHERE id = %s", (client.plan_id,))
    plan = database.cur.fetchone()
    if not plan:
        raise HTTPException(status_code=400, detail="Invalid plan ID")

    duration = plan[0]
    end_date = client.start_date + timedelta(days=duration)

    database.cur.execute("""
        UPDATE clients
        SET clientname = %s, phonenumber = %s, dateofbirth = %s, gender = %s,
            bloodgroup = %s, address = %s, notes = %s, email = %s,
            height = %s, weight = %s, plan_id = %s, start_date = %s, end_date = %s
        WHERE id = %s
        RETURNING id
    """, (
        client.clientname, client.phonenumber, client.dateofbirth, client.gender,
        client.bloodgroup, client.address, client.notes, client.email,
        client.height, client.weight, client.plan_id, client.start_date, end_date,
        client_id
    ))
    database.conn.commit()
    if database.cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Client updated successfully", "end_date": str(end_date)}

# ✅ Delete client(deleting client we can add it in delete option)
@app.delete("/clients/{client_id}")
def delete_client(client_id: int):
    database.cur.execute("DELETE FROM clients WHERE id = %s RETURNING id", (client_id,))
    database.conn.commit()
    if database.cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="client not found")
    return {"message": "client deleted successfully"}


#PLANS

class plan(BaseModel):
    planname: str
    days: int
    amount: float
    

# ✅ Create plan (add plan page)
@app.post("/plans/")
def create_plan(plan: plan):
    try:
        database.cur.execute(
            "INSERT INTO plans (planname,days,amount) VALUES (%s,%s,%s) RETURNING id",
            (plan.planname, plan.days, plan.amount),
        )
        database.conn.commit()
        plan_id = database.cur.fetchone()[0]
        return {"id": plan_id, "message": "plan created successfully"}
    except Exception as e:
        database.conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# ✅ Read All plans(total plans)
@app.get("/plans/")
def get_plans():
    database.cur.execute("SELECT id,planname,days,amount FROM plans order by id")
    rows = database.cur.fetchall()
    plans = []
    for row in rows:
        plans.append({
            "id": row[0],
            "planname": row[1],
            "days": row[2],
            "amount": float(row[3]) if row[3] else None,
        })
    return {"plans": plans}

# ✅ Update plans(updating create plan details we can add it in edit option)
@app.put("/plans/{plan_id}")
def update_plan(plan_id: int, plan: plan):
    database.cur.execute(
        "UPDATE plans SET planname = %s, days = %s, amount = %s WHERE id = %s RETURNING id",
        (plan.planname, plan.days, plan.amount, plan_id),
    )
    database.conn.commit()
    if database.cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="plan not found")
    return {"message": "plan updated successfully"}

# ✅ Delete plans(deleting plan we can add it in delete option)
@app.delete("/plans/{plan_id}")
def delete_plan(plan_id: int):
    database.cur.execute("DELETE FROM plans WHERE id = %s RETURNING id", (plan_id,))
    database.conn.commit()
    if database.cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="plan not found")
    return {"message": "plan deleted successfully"}

#STAFFS

class staffs(BaseModel):
    staffname: str
    email: str
    phonenumber: int
    role: str

# ✅ Create staffs (add staffs page)
@app.post("/staffs/")
def create_staffs(staffs: staffs):
    try:
        database.cur.execute(
            "INSERT INTO staffs (staffname,email,phonenumber,role) VALUES (%s,%s,%s,%s) RETURNING id",
            (staffs.staffname, staffs.email, staffs.phonenumber, staffs.role),
        )
        database.conn.commit()
        plan_id = database.cur.fetchone()[0]
        return {"id": plan_id, "message": "staffs added successfully"}
    except Exception as e:
        database.conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# ✅ Read All staffs(total staffs)
@app.get("/staffs/")
def get_staffs():
    database.cur.execute("SELECT id,staffname,email,phonenumber,role FROM staffs")
    rows = database.cur.fetchall()
    staffs = []
    for row in rows:
        staffs.append({
            "id": row[0],
            "staffname": row[1],
            "email": row[2],
            "phonenumber": str(row[3]),
            "role": row[4],
        })
    return {"staffs": staffs}

# ✅ Update staffs(updating staffs details we can add it in edit option)
@app.put("/staffs/{staffs_id}")
def update_staffs(staffs_id: int, staffs: staffs):
    database.cur.execute(
        "UPDATE staffs SET staffname = %s, email = %s, phonenumber = %s, role = %s WHERE id = %s RETURNING id",
        (staffs.staffname, staffs.email, staffs.phonenumber, staffs.role, staffs_id),
    )
    database.conn.commit()
    if database.cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="staffs not found")
    return {"message": "staffs updated successfully"}

# ✅ Delete staffs(deleting staffs we can add it in delete option)
@app.delete("/staffs/{staffs_id}")
def delete_staffs(staffs_id: int):
    database.cur.execute("DELETE FROM staffs WHERE id = %s RETURNING id", (staffs_id,))
    database.conn.commit()
    if database.cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="staffs not found")
    return {"message": "staffs deleted successfully"}


#Dashboard stats

@app.get("/dashboard/stats")
def dashboard_stats():
    database.cur.execute("SELECT COUNT(*) FROM clients")
    total = database.cur.fetchone()[0]

    database.cur.execute("SELECT COUNT(*) FROM clients WHERE end_date >= CURRENT_DATE")
    active = database.cur.fetchone()[0]

    database.cur.execute("SELECT COUNT(*) FROM clients WHERE end_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '10 days'")
    expiring_10 = database.cur.fetchone()[0]

    database.cur.execute("SELECT COUNT(*) FROM clients WHERE end_date < CURRENT_DATE AND end_date >= CURRENT_DATE - INTERVAL '30 days'")
    expired_30 = database.cur.fetchone()[0]

    return {
        "total_members": total,
        "active_members": active,
        "expiring_in_10_days": expiring_10,
        "expired_in_last_30_days": expired_30
    }

#dashboard card details where if i click the box i will see the details of the clients based on their status

@app.get("/clients/filter/")
def filter_clients(status: str = Query(..., regex="^(active|expiring|expired)$")):
    if status == "active":
        query = """
            SELECT c.id, c.clientname, c.phonenumber, c.email, c.start_date, c.end_date,
                   p.planname, p.days, p.amount
            FROM clients c
            JOIN plans p ON c.plan_id = p.id
            WHERE c.end_date >= CURRENT_DATE
            ORDER BY c.end_date
        """
    elif status == "expiring":
        query = """
            SELECT c.id, c.clientname, c.phonenumber, c.email, c.start_date, c.end_date,
                   p.planname, p.days, p.amount
            FROM clients c
            JOIN plans p ON c.plan_id = p.id
            WHERE c.end_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '10 days'
            ORDER BY c.end_date
        """
    elif status == "expired":
        query = """
            SELECT c.id, c.clientname, c.phonenumber, c.email, c.start_date, c.end_date,
                   p.planname, p.days, p.amount
            FROM clients c
            JOIN plans p ON c.plan_id = p.id
            WHERE c.end_date < CURRENT_DATE
              AND c.end_date >= CURRENT_DATE - INTERVAL '30 days'
            ORDER BY c.end_date
        """
    else:
        raise HTTPException(status_code=400, detail="Invalid status")

    database.cur.execute(query)
    rows = database.cur.fetchall()
    clients = []
    for row in rows:
        clients.append({
            "id": row[0],
            "clientname": row[1],
            "phonenumber": str(row[2]),
            "email": row[3],
            "start_date": str(row[4]),
            "end_date": str(row[5]) if row[5] else None,
            "planname": row[6],
            "days": row[7],
            "amount": float(row[8]) if row[8] else None,
        })
    return {"status": status, "clients": clients}

#leads

class Lead(BaseModel):
    name: str
    phonenumber: str
    notes: Optional[str] = None


@app.post("/leads/")
def create_lead(lead: Lead):
    try:
        database.cur.execute(
            "INSERT INTO leads (name, phonenumber, notes) VALUES (%s, %s, %s) RETURNING id",
            (lead.name, lead.phonenumber, lead.notes)
        )
        database.conn.commit()
        lead_id = database.cur.fetchone()[0]
        return {"id": lead_id, "message": "Lead added successfully"}
    except Exception as e:
        database.conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/leads/")
def get_leads():
    database.cur.execute("SELECT id, name, phonenumber, notes, created_at FROM leads ORDER BY created_at DESC")
    rows = database.cur.fetchall()
    leads = []
    for row in rows:
        leads.append({
            "id": row[0],
            "name": row[1],
            "phonenumber": str(row[2]),
            "notes": row[3],
            "created_at": str(row[4]) if row[4] else None,
        })
    return {"leads": leads}

@app.delete("/leads/{lead_id}")
def delete_lead(lead_id: int):
    database.cur.execute("DELETE FROM leads WHERE id = %s RETURNING id", (lead_id,))
    database.conn.commit()
    if database.cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"message": "Lead deleted successfully"}
