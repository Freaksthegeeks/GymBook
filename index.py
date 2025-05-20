from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from config import database  # Import database connection

app = FastAPI()

# ✅ User Model (Request Body)
class User(BaseModel):
    username: str
    email: str
    password: str

# ✅ Create User
@app.post("/users/")
def create_user(user: User):
    try:
        database.cur.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s) RETURNING id",
            (user.username, user.email, user.password),
        )
        database.conn.commit()
        user_id = database.cur.fetchone()[0]
        return {"id": user_id, "message": "User created successfully"}
    except Exception as e:
        database.conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# ✅ Read All Users
@app.get("/users/")
def get_users():
    database.cur.execute("SELECT id, username, email FROM users")
    users = database.cur.fetchall()
    return {"users": users}

# ✅ Read Single User
@app.get("/users/{user_id}")
def get_user(user_id: int):
    database.cur.execute("SELECT id, username, email FROM users WHERE id = %s", (user_id,))
    user = database.cur.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user[0], "username": user[1], "email": user[2]}

# ✅ Update User
@app.put("/users/{user_id}")
def update_user(user_id: int, user: User):
    database.cur.execute(
        "UPDATE users SET username = %s, email = %s, password = %s WHERE id = %s RETURNING id",
        (user.username, user.email, user.password, user_id),
    )
    database.conn.commit()
    if database.cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated successfully"}

# ✅ Delete User
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    database.cur.execute("DELETE FROM users WHERE id = %s RETURNING id", (user_id,))
    database.conn.commit()
    if database.cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
