from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from config import database
from fastapi import Depends
from index import get_current_user, get_current_gym_id

router = APIRouter()


class StaffModel(BaseModel):
    staffname: str
    email: str
    phonenumber: int
    role: str


@router.post("/staffs/")
def create_staffs(staffs: StaffModel, current_gym_id: int = Depends(get_current_gym_id)):
    try:
        database.cur.execute(
            "INSERT INTO staffs (staffname,email,phonenumber,role,gym_id) VALUES (%s,%s,%s,%s,%s) RETURNING id",
            (staffs.staffname, staffs.email, staffs.phonenumber, staffs.role, current_gym_id),
        )
        database.conn.commit()
        staff_id = database.cur.fetchone()[0]
        return {"id": staff_id, "message": "staffs added successfully"}
    except Exception as e:
        database.conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/staffs/")
def get_staffs(current_gym_id: int = Depends(get_current_gym_id)):
    database.cur.execute("SELECT id,staffname,email,phonenumber,role FROM staffs WHERE gym_id = %s", (current_gym_id,))
    rows = database.cur.fetchall()
    staffs = []
    for row in rows:
        staffs.append({
            "id": row[0],
            "staffname": row[1],
            "email": row[2],
            "phonenumber": int(row[3]),
            "role": row[4],
        })
    return {"staffs": staffs}


@router.put("/staffs/{staffs_id}")
def update_staffs(staffs_id: int, staffs: StaffModel, current_gym_id: int = Depends(get_current_gym_id)):
    database.cur.execute(
        "UPDATE staffs SET staffname = %s, email = %s, phonenumber = %s, role = %s WHERE id = %s AND gym_id = %s RETURNING id",
        (staffs.staffname, staffs.email, staffs.phonenumber, staffs.role, staffs_id, current_gym_id),
    )
    database.conn.commit()
    if database.cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="staffs not found")
    return {"message": "staffs updated successfully"}


@router.delete("/staffs/{staffs_id}")
def delete_staffs(staffs_id: int, current_gym_id: int = Depends(get_current_gym_id)):
    database.cur.execute("DELETE FROM staffs WHERE id = %s AND gym_id = %s RETURNING id", (staffs_id, current_gym_id))
    database.conn.commit()
    if database.cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="staffs not found")
    return {"message": "staffs deleted successfully"}
