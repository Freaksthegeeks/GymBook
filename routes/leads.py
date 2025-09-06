from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
from config import database

router = APIRouter()


class LeadModel(BaseModel):
    name: str
    phonenumber: str
    notes: Optional[str] = None


@router.post("/leads/")
def create_lead(lead: LeadModel):
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


@router.get("/leads/")
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


@router.delete("/leads/{lead_id}")
def delete_lead(lead_id: int):
    database.cur.execute("DELETE FROM leads WHERE id = %s RETURNING id", (lead_id,))
    database.conn.commit()
    if database.cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"message": "Lead deleted successfully"}
