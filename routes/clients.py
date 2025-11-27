from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date, timedelta
from pydantic import BaseModel
from config import database

router = APIRouter()


class ClientModel(BaseModel):
    clientname: str
    phonenumber: int
    dateofbirth: str
    gender: str
    bloodgroup: str
    address: str
    notes: Optional[str] = None
    email: str
    height: float
    weight: float
    plan_id: int
    start_date: date = date.today()


@router.post("/clients/")
def create_client(client: ClientModel):
    try:
        database.cur.execute("SELECT days, amount FROM plans WHERE id = %s", (client.plan_id,))
        plan = database.cur.fetchone()
        if not plan:
            raise HTTPException(status_code=400, detail="Invalid plan ID")

        duration = plan[0]
        plan_amount = float(plan[1]) if plan[1] else 0.0
        end_date = client.start_date + timedelta(days=duration)

        database.cur.execute("""
            INSERT INTO clients
                (clientname, phonenumber, dateofbirth, gender, bloodgroup,
                 address, notes, email, height, weight,
                 plan_id, start_date, end_date, balance_due)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id
        """, (
            client.clientname, client.phonenumber, client.dateofbirth,
            client.gender, client.bloodgroup, client.address, client.notes,
            client.email, client.height, client.weight,
            client.plan_id, client.start_date, end_date, plan_amount
        ))
        database.conn.commit()
        client_id = database.cur.fetchone()[0]
        return {"id": client_id, "end_date": str(end_date), "message": "Client created successfully"}

    except Exception as e:
        database.conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/clients/")
def get_clients():
    database.cur.execute("""
        SELECT c.id, c.clientname, c.phonenumber, c.dateofbirth, c.gender, c.bloodgroup,
               c.address, c.notes, c.email, c.height, c.weight,
               c.start_date, c.end_date, c.total_paid, c.balance_due,
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
            "total_paid": float(row[13]) if row[13] else 0.0,
            "balance_due": float(row[14]) if row[14] else 0.0,
            "planname": row[15],
            "days": row[16],
            "amount": float(row[17]) if row[17] else None,
        })
    return {"clients": clients}


@router.get("/clients/birthdays/today")
def get_birthday_clients():
    database.cur.execute("""
        SELECT c.id, c.clientname, c.phonenumber, c.dateofbirth, c.gender, c.bloodgroup,
               c.address, c.notes, c.email, c.height, c.weight,
               c.start_date, c.end_date, c.total_paid, c.balance_due,
               p.planname, p.days, p.amount
        FROM clients c
        JOIN plans p ON c.plan_id = p.id
        WHERE EXTRACT(MONTH FROM c.dateofbirth::date) = EXTRACT(MONTH FROM CURRENT_DATE)
          AND EXTRACT(DAY FROM c.dateofbirth::date) = EXTRACT(DAY FROM CURRENT_DATE)
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
            "total_paid": float(row[13]) if row[13] else 0.0,
            "balance_due": float(row[14]) if row[14] else 0.0,
            "planname": row[15],
            "days": row[16],
            "amount": float(row[17]) if row[17] else None,
        })
    return {"clients": clients}


@router.get("/clients/{client_id}")
def get_client(client_id: int):
    database.cur.execute("""
        SELECT c.id, c.clientname, c.phonenumber, c.dateofbirth, c.gender, c.bloodgroup,
               c.address, c.notes, c.email, c.height, c.weight,
               c.start_date, c.end_date, c.total_paid, c.balance_due,
               p.planname, p.days, p.amount
        FROM clients c
        JOIN plans p ON c.plan_id = p.id
        WHERE c.id = %s
    """, (client_id,))
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
        "start_date": str(row[11]),
        "end_date": str(row[12]) if row[12] else None,
        "total_paid": float(row[13]) if row[13] else 0.0,
        "balance_due": float(row[14]) if row[14] else 0.0,
        "planname": row[15],
        "days": row[16],
        "amount": float(row[17]) if row[17] else None,
    }
    return {"client": client}


@router.put("/clients/{client_id}")
def update_client(client_id: int, client: ClientModel):
    database.cur.execute("SELECT days, amount FROM plans WHERE id = %s", (client.plan_id,))
    plan = database.cur.fetchone()
    if not plan:
        raise HTTPException(status_code=400, detail="Invalid plan ID")

    duration = plan[0]
    plan_amount = float(plan[1]) if plan[1] else 0.0
    end_date = client.start_date + timedelta(days=duration)

    database.cur.execute("""
        UPDATE clients
        SET clientname = %s, phonenumber = %s, dateofbirth = %s, gender = %s,
            bloodgroup = %s, address = %s, notes = %s, email = %s,
            height = %s, weight = %s, plan_id = %s, start_date = %s, end_date = %s,
            balance_due = %s
        WHERE id = %s
        RETURNING id
    """, (
        client.clientname, client.phonenumber, client.dateofbirth, client.gender,
        client.bloodgroup, client.address, client.notes, client.email,
        client.height, client.weight, client.plan_id, client.start_date, end_date,
        plan_amount, client_id
    ))
    database.conn.commit()
    if database.cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Client updated successfully", "end_date": str(end_date)}


@router.delete("/clients/{client_id}")
def delete_client(client_id: int):
    database.cur.execute("DELETE FROM clients WHERE id = %s RETURNING id", (client_id,))
    database.conn.commit()
    if database.cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="client not found")
    return {"message": "client deleted successfully"}


@router.get("/clients/filter/")
def filter_clients(status: str = Query(..., regex="^(active|expiring|expired)$")):
    if status == "active":
        query = """
            SELECT c.id, c.clientname, c.phonenumber, c.dateofbirth, c.gender, c.bloodgroup,
                   c.address, c.notes, c.email, c.height, c.weight,
                   c.start_date, c.end_date, c.total_paid, c.balance_due,
                   p.planname, p.days, p.amount
            FROM clients c
            JOIN plans p ON c.plan_id = p.id
            WHERE c.end_date >= CURRENT_DATE
            ORDER BY c.end_date
        """
    elif status == "expiring":
        query = """
            SELECT c.id, c.clientname, c.phonenumber, c.dateofbirth, c.gender, c.bloodgroup,
                   c.address, c.notes, c.email, c.height, c.weight,
                   c.start_date, c.end_date, c.total_paid, c.balance_due,
                   p.planname, p.days, p.amount
            FROM clients c
            JOIN plans p ON c.plan_id = p.id
            WHERE c.end_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '10 days'
            ORDER BY c.end_date
        """
    elif status == "expired":
        query = """
                SELECT c.id, c.clientname, c.phonenumber, c.dateofbirth, c.gender, c.bloodgroup,
                             c.address, c.notes, c.email, c.height, c.weight,
                             c.start_date, c.end_date, c.total_paid, c.balance_due,
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
            "dateofbirth": str(row[3]) if row[3] else None,
            "gender": row[4],
            "bloodgroup": row[5],
            "address": row[6],
            "notes": row[7],
            "email": row[8],
            "height": float(row[9]) if row[9] else None,
            "weight": float(row[10]) if row[10] else None,
            "start_date": str(row[11]),
            "end_date": str(row[12]) if row[12] else None,
            "total_paid": float(row[13]) if row[13] else 0.0,
            "balance_due": float(row[14]) if row[14] else 0.0,
            "planname": row[15],
            "days": row[16],
            "amount": float(row[17]) if row[17] else None,
        })
    return {"status": status, "clients": clients}