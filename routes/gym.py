from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from config import database
from typing import List
import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from index import get_current_user, SECRET_KEY, ALGORITHM

router = APIRouter()

security = HTTPBearer()

class GymCreate(BaseModel):
    name: str
    description: str = None
    address: str = None
    phone: str = None
    email: str = None

class GymSwitch(BaseModel):
    gym_id: int

class Gym(BaseModel):
    id: int
    name: str
    description: str = None
    address: str = None
    phone: str = None
    email: str = None
    created_at: str
    updated_at: str

@router.post("/gyms/", response_model=dict)
def create_gym(gym: GymCreate, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["user_id"]
        
        # Create the gym
        database.cur.execute("""
            INSERT INTO gyms (name, description, address, phone, email)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (gym.name, gym.description, gym.address, gym.phone, gym.email))
        
        gym_id = database.cur.fetchone()[0]
        
        # Add the user as owner of the new gym
        database.cur.execute("""
            INSERT INTO user_gyms (user_id, gym_id, role, is_owner)
            VALUES (%s, %s, %s, %s)
        """, (user_id, gym_id, 'admin', True))
        
        database.conn.commit()
        
        return {
            "message": "Gym created successfully",
            "gym_id": gym_id
        }
    except Exception as e:
        database.conn.rollback()
        raise HTTPException(status_code=500, detail=f"Gym creation failed: {str(e)}")

@router.get("/gyms/", response_model=List[Gym])
def get_user_gyms(current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["user_id"]
        
        database.cur.execute("""
            SELECT g.id, g.name, g.description, g.address, g.phone, g.email, 
                   g.created_at, g.updated_at
            FROM gyms g
            JOIN user_gyms ug ON g.id = ug.gym_id
            WHERE ug.user_id = %s
            ORDER BY ug.is_owner DESC, g.name
        """, (user_id,))
        
        gyms = []
        for row in database.cur.fetchall():
            gyms.append(Gym(
                id=row[0],
                name=row[1],
                description=row[2],
                address=row[3],
                phone=row[4],
                email=row[5],
                created_at=str(row[6]),
                updated_at=str(row[7])
            ))
        
        return gyms
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get gyms: {str(e)}")

@router.post("/gyms/switch/", response_model=dict)
def switch_gym(gym_switch: GymSwitch, credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        # First verify user has access to the gym
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        gym_id = gym_switch.gym_id
        
        # Check if user has access to this gym
        database.cur.execute("""
            SELECT COUNT(*) FROM user_gyms 
            WHERE user_id = %s AND gym_id = %s
        """, (user_id, gym_id))
        
        if database.cur.fetchone()[0] == 0:
            raise HTTPException(status_code=403, detail="You don't have access to this gym")
        
        # Update the token with the new current gym
        # In a real implementation, we'd return a new token with updated gym context
        # For now, we'll just return success and the frontend will handle the context
        
        return {
            "message": "Gym switched successfully",
            "gym_id": gym_id
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gym switch failed: {str(e)}")

@router.get("/gyms/current/", response_model=Gym)
def get_current_gym(current_user: dict = Depends(get_current_user)):
    try:
        current_gym_id = current_user.get("current_gym_id")
        if not current_gym_id:
            raise HTTPException(status_code=404, detail="No current gym selected")
        
        database.cur.execute("""
            SELECT id, name, description, address, phone, email, created_at, updated_at
            FROM gyms
            WHERE id = %s
        """, (current_gym_id,))
        
        gym_data = database.cur.fetchone()
        if not gym_data:
            raise HTTPException(status_code=404, detail="Current gym not found")
        
        return Gym(
            id=gym_data[0],
            name=gym_data[1],
            description=gym_data[2],
            address=gym_data[3],
            phone=gym_data[4],
            email=gym_data[5],
            created_at=str(gym_data[6]),
            updated_at=str(gym_data[7])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get current gym: {str(e)}")