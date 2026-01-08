from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from config import database  # Import database connection
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import jwt


app = FastAPI()

# Serve static files
app.mount("/styles", StaticFiles(directory="web/styles"), name="styles")
app.mount("/scripts", StaticFiles(directory="web/scripts"), name="scripts")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

# Authentication Utility Functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        current_gym_id: int = payload.get("current_gym_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"user_id": user_id, "current_gym_id": current_gym_id}
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


def get_current_gym_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Helper function to extract only the current gym ID from the token
    """
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        current_gym_id: int = payload.get("current_gym_id")
        if current_gym_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No gym selected. Please select a gym first."
            )
        return current_gym_id
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


# Authentication Endpoints (keep here)


@app.post("/register/", response_model=dict)
def register_user(user: UserRegister):
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

        # Get the user's first gym as the default current gym
        database.cur.execute("""
            SELECT gym_id FROM user_gyms 
            WHERE user_id = %s 
            ORDER BY is_owner DESC, id ASC
            LIMIT 1
        """, (user_id,))
        
        gym_result = database.cur.fetchone()
        current_gym_id = gym_result[0] if gym_result else None
        
        # If user has no gyms, return a special response to indicate onboarding
        if current_gym_id is None:
            # Check if user has any gyms at all
            database.cur.execute("SELECT COUNT(*) FROM user_gyms WHERE user_id = %s", (user_id,))
            gym_count = database.cur.fetchone()[0]
            if gym_count == 0:
                # User has no gyms, need to go through onboarding
                pass  # current_gym_id remains None, which is fine for onboarding
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_id, "username": username, "current_gym_id": current_gym_id},
            expires_delta=access_token_expires
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user_id,
            username=username
        )

    except HTTPException:
        database.conn.rollback()  # Rollback in case of HTTPException
        raise
    except Exception as e:
        database.conn.rollback()  # Rollback in case of any other exception
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@app.get("/me/", response_model=dict)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["user_id"]
        database.cur.execute("""
            SELECT id, username, email, created_at FROM loggingcredentials 
            WHERE id = %s
        """, (user_id,))

        user_data = database.cur.fetchone()
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "id": user_data[0],
            "username": user_data[1],
            "email": user_data[2],
            "created_at": str(user_data[3]),
            "current_gym_id": current_user["current_gym_id"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user info: {str(e)}")


# Import routes after all functions are defined
from routes import clients, plans, staffs, leads, dashboard, payments, reports, gym

# Include routers
app.include_router(clients.router)
app.include_router(plans.router)
app.include_router(staffs.router)
app.include_router(leads.router)
app.include_router(dashboard.router)
app.include_router(payments.router)
app.include_router(reports.router)
app.include_router(gym.router)

# Serve the main index.html file
@app.get("/")
async def read_index():
    return FileResponse('web/index.html')