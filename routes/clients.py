from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date, timedelta
from pydantic import BaseModel
from config import database
from fastapi import HTTPException, Depends
from index import get_current_user, get_current_gym_id

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


class ClientUpdateModel(BaseModel):
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


class RenewalModel(BaseModel):
    plan_id: int
    start_date: date = date.today()


@router.post("/clients/")
def create_client(client: ClientModel, current_gym_id: int = Depends(get_current_gym_id)):
    try:
        database.cur.execute("SELECT days, amount FROM plans WHERE id = %s AND gym_id = %s", (client.plan_id, current_gym_id))
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
                 plan_id, start_date, end_date, balance_due, gym_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id
        """, (
            client.clientname, client.phonenumber, client.dateofbirth,
            client.gender, client.bloodgroup, client.address, client.notes,
            client.email, client.height, client.weight,
            client.plan_id, client.start_date, end_date, plan_amount, current_gym_id
        ))
        database.conn.commit()
        client_id = database.cur.fetchone()[0]
        return {"id": client_id, "end_date": str(end_date), "message": "Client created successfully"}

    except Exception as e:
        database.conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/clients/")
def get_clients(current_gym_id: int = Depends(get_current_gym_id)):
    database.cur.execute("""
        SELECT c.id, c.clientname, c.phonenumber, c.dateofbirth, c.gender, c.bloodgroup,
               c.address, c.notes, c.email, c.height, c.weight,
               c.start_date, c.end_date, c.total_paid, c.balance_due,
               p.planname, p.days, p.amount
        FROM clients c
        LEFT JOIN plans p ON c.plan_id = p.id
        WHERE c.gym_id = %s
    """, (current_gym_id,))
    rows = database.cur.fetchall()
    clients = []
    for row in rows:
        # Ensure we have enough elements in the row
        if len(row) >= 18:
            clients.append({
                "id": row[0] if row[0] is not None else 0,
                "clientname": row[1] if row[1] else "",
                "phonenumber": str(row[2]) if row[2] else "",
                "dateofbirth": str(row[3]) if row[3] else None,
                "gender": row[4] if row[4] else "",
                "bloodgroup": row[5] if row[5] else "",
                "address": row[6] if row[6] else "",
                "notes": row[7] if row[7] else "",
                "email": row[8] if row[8] else "",
                "height": float(row[9]) if row[9] is not None else 0.0,
                "weight": float(row[10]) if row[10] is not None else 0.0,
                "start_date": str(row[11]) if row[11] else None,
                "end_date": str(row[12]) if row[12] else None,
                "total_paid": float(row[13]) if row[13] is not None else 0.0,
                "balance_due": float(row[14]) if row[14] is not None else 0.0,
                "planname": row[15] if row[15] else "",
                "days": row[16] if row[16] is not None else 0,
                "amount": float(row[17]) if row[17] is not None else 0.0,
            })
        else:
            # Handle case where row doesn't have enough elements
            clients.append({
                "id": row[0] if len(row) > 0 and row[0] is not None else 0,
                "clientname": row[1] if len(row) > 1 and row[1] else "",
                "phonenumber": str(row[2]) if len(row) > 2 and row[2] else "",
                "dateofbirth": str(row[3]) if len(row) > 3 and row[3] else None,
                "gender": row[4] if len(row) > 4 and row[4] else "",
                "bloodgroup": row[5] if len(row) > 5 and row[5] else "",
                "address": row[6] if len(row) > 6 and row[6] else "",
                "notes": row[7] if len(row) > 7 and row[7] else "",
                "email": row[8] if len(row) > 8 and row[8] else "",
                "height": float(row[9]) if len(row) > 9 and row[9] is not None else 0.0,
                "weight": float(row[10]) if len(row) > 10 and row[10] is not None else 0.0,
                "start_date": str(row[11]) if len(row) > 11 and row[11] else None,
                "end_date": str(row[12]) if len(row) > 12 and row[12] else None,
                "total_paid": float(row[13]) if len(row) > 13 and row[13] is not None else 0.0,
                "balance_due": float(row[14]) if len(row) > 14 and row[14] is not None else 0.0,
                "planname": row[15] if len(row) > 15 and row[15] else "",
                "days": row[16] if len(row) > 16 and row[16] is not None else 0,
                "amount": float(row[17]) if len(row) > 17 and row[17] is not None else 0.0,
            })
    return {"clients": clients}


@router.get("/clients/birthdays/today")
def get_birthday_clients(current_gym_id: int = Depends(get_current_gym_id)):
    database.cur.execute("""
        SELECT c.id, c.clientname, c.phonenumber, c.dateofbirth, c.gender, c.bloodgroup,
               c.address, c.notes, c.email, c.height, c.weight,
               c.start_date, c.end_date, c.total_paid, c.balance_due,
               p.planname, p.days, p.amount
        FROM clients c
        LEFT JOIN plans p ON c.plan_id = p.id
        WHERE EXTRACT(MONTH FROM c.dateofbirth::date) = EXTRACT(MONTH FROM CURRENT_DATE)
          AND EXTRACT(DAY FROM c.dateofbirth::date) = EXTRACT(DAY FROM CURRENT_DATE)
          AND c.gym_id = %s
    """, (current_gym_id,))
    rows = database.cur.fetchall()
    clients = []
    for row in rows:
        # Ensure we have enough elements in the row
        if len(row) >= 18:
            clients.append({
                "id": row[0] if row[0] is not None else 0,
                "clientname": row[1] if row[1] else "",
                "phonenumber": str(row[2]) if row[2] else "",
                "dateofbirth": str(row[3]) if row[3] else None,
                "gender": row[4] if row[4] else "",
                "bloodgroup": row[5] if row[5] else "",
                "address": row[6] if row[6] else "",
                "notes": row[7] if row[7] else "",
                "email": row[8] if row[8] else "",
                "height": float(row[9]) if row[9] is not None else 0.0,
                "weight": float(row[10]) if row[10] is not None else 0.0,
                "start_date": str(row[11]) if row[11] else None,
                "end_date": str(row[12]) if row[12] else None,
                "total_paid": float(row[13]) if row[13] is not None else 0.0,
                "balance_due": float(row[14]) if row[14] is not None else 0.0,
                "planname": row[15] if row[15] else "",
                "days": row[16] if row[16] is not None else 0,
                "amount": float(row[17]) if row[17] is not None else 0.0,
            })
        else:
            # Handle case where row doesn't have enough elements
            clients.append({
                "id": row[0] if len(row) > 0 and row[0] is not None else 0,
                "clientname": row[1] if len(row) > 1 and row[1] else "",
                "phonenumber": str(row[2]) if len(row) > 2 and row[2] else "",
                "dateofbirth": str(row[3]) if len(row) > 3 and row[3] else None,
                "gender": row[4] if len(row) > 4 and row[4] else "",
                "bloodgroup": row[5] if len(row) > 5 and row[5] else "",
                "address": row[6] if len(row) > 6 and row[6] else "",
                "notes": row[7] if len(row) > 7 and row[7] else "",
                "email": row[8] if len(row) > 8 and row[8] else "",
                "height": float(row[9]) if len(row) > 9 and row[9] is not None else 0.0,
                "weight": float(row[10]) if len(row) > 10 and row[10] is not None else 0.0,
                "start_date": str(row[11]) if len(row) > 11 and row[11] else None,
                "end_date": str(row[12]) if len(row) > 12 and row[12] else None,
                "total_paid": float(row[13]) if len(row) > 13 and row[13] is not None else 0.0,
                "balance_due": float(row[14]) if len(row) > 14 and row[14] is not None else 0.0,
                "planname": row[15] if len(row) > 15 and row[15] else "",
                "days": row[16] if len(row) > 16 and row[16] is not None else 0,
                "amount": float(row[17]) if len(row) > 17 and row[17] is not None else 0.0,
            })
    return {"clients": clients}


@router.get("/clients/{client_id}")
def get_client(client_id: int, current_gym_id: int = Depends(get_current_gym_id)):
    database.cur.execute("""
        SELECT c.id, c.clientname, c.phonenumber, c.dateofbirth, c.gender, c.bloodgroup,
               c.address, c.notes, c.email, c.height, c.weight,
               c.start_date, c.end_date, c.total_paid, c.balance_due,
               p.planname, p.days, p.amount
        FROM clients c
        JOIN plans p ON c.plan_id = p.id
        WHERE c.id = %s AND c.gym_id = %s
    """, (client_id, current_gym_id))
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
def update_client(client_id: int, client: ClientUpdateModel, current_gym_id: int = Depends(get_current_gym_id)):
    # Get current client data to preserve plan information
    database.cur.execute("SELECT plan_id, start_date FROM clients WHERE id = %s AND gym_id = %s", (client_id, current_gym_id))
    current_client = database.cur.fetchone()
    if not current_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    current_plan_id = current_client[0]
    current_start_date = current_client[1]
    
    # Get plan data to calculate end date
    database.cur.execute("SELECT days FROM plans WHERE id = %s AND gym_id = %s", (current_plan_id, current_gym_id))
    plan = database.cur.fetchone()
    if not plan:
        raise HTTPException(status_code=400, detail="Invalid plan ID")
    
    duration = plan[0]
    end_date = current_start_date + timedelta(days=duration)
    
    # Convert phone number to integer
    try:
        phone_number = int(client.phonenumber)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid phone number")
    
    # Update client while preserving plan and payment status
    database.cur.execute("""
        UPDATE clients
        SET clientname = %s, phonenumber = %s, dateofbirth = %s, gender = %s,
            bloodgroup = %s, address = %s, notes = %s, email = %s,
            height = %s, weight = %s, end_date = %s
        WHERE id = %s AND gym_id = %s
        RETURNING id
    """, (
        client.clientname, phone_number, client.dateofbirth, client.gender,
        client.bloodgroup, client.address, client.notes, client.email,
        client.height, client.weight, end_date, client_id, current_gym_id
    ))
    
    database.conn.commit()
    if database.cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Client updated successfully", "end_date": str(end_date)}


@router.post("/clients/{client_id}/renew")
def renew_subscription(client_id: int, renewal: RenewalModel, current_gym_id: int = Depends(get_current_gym_id)):
    try:
        # Get current client data
        database.cur.execute("""
            SELECT c.clientname, c.plan_id, p.amount
            FROM clients c
            LEFT JOIN plans p ON c.plan_id = p.id
            WHERE c.id = %s AND c.gym_id = %s
        """, (client_id, current_gym_id))
        client_data = database.cur.fetchone()
        if not client_data:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get new plan data
        database.cur.execute("SELECT days, amount FROM plans WHERE id = %s AND gym_id = %s", (renewal.plan_id, current_gym_id))
        plan = database.cur.fetchone()
        if not plan:
            raise HTTPException(status_code=400, detail="Invalid plan ID")
        
        duration = plan[0]
        plan_amount = float(plan[1]) if plan[1] else 0.0
        end_date = renewal.start_date + timedelta(days=duration)
        
        # Update client with new plan and reset payment status
        database.cur.execute("""
            UPDATE clients
            SET plan_id = %s, start_date = %s, end_date = %s,
                total_paid = 0, balance_due = %s
            WHERE id = %s AND gym_id = %s
        """, (renewal.plan_id, renewal.start_date, end_date, plan_amount, client_id, current_gym_id))
        
        database.conn.commit()
        return {
            "message": "Subscription renewed successfully", 
            "client_id": client_id,
            "plan_id": renewal.plan_id,
            "start_date": str(renewal.start_date),
            "end_date": str(end_date),
            "amount": plan_amount
        }
    except Exception as e:
        database.conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/clients/{client_id}")
def delete_client(client_id: int, current_gym_id: int = Depends(get_current_gym_id)):
    database.cur.execute("DELETE FROM clients WHERE id = %s AND gym_id = %s RETURNING id", (client_id, current_gym_id))
    database.conn.commit()
    if database.cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="client not found")
    return {"message": "client deleted successfully"}


@router.get("/clients/filter/")
def filter_clients(status: str = Query(..., regex="^(active|expiring|expired)$"), current_gym_id: int = Depends(get_current_gym_id)):
    if status == "active":
        query = '''
            SELECT c.id, c.clientname, c.phonenumber, c.dateofbirth, c.gender, c.bloodgroup,
                   c.address, c.notes, c.email, c.height, c.weight,
                   c.start_date, c.end_date, c.total_paid, c.balance_due,
                   p.planname, p.days, p.amount
            FROM clients c
            JOIN plans p ON c.plan_id = p.id
            WHERE c.end_date >= CURRENT_DATE AND c.gym_id = %s
            ORDER BY c.end_date
        '''
    elif status == "expiring":
        query = '''
            SELECT c.id, c.clientname, c.phonenumber, c.dateofbirth, c.gender, c.bloodgroup,
                   c.address, c.notes, c.email, c.height, c.weight,
                   c.start_date, c.end_date, c.total_paid, c.balance_due,
                   p.planname, p.days, p.amount
            FROM clients c
            JOIN plans p ON c.plan_id = p.id
            WHERE c.end_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '10 days'
                AND c.gym_id = %s
            ORDER BY c.end_date
        '''
    elif status == "expired":
        query = '''
                SELECT c.id, c.clientname, c.phonenumber, c.dateofbirth, c.gender, c.bloodgroup,
                             c.address, c.notes, c.email, c.height, c.weight,
                             c.start_date, c.end_date, c.total_paid, c.balance_due,
                             p.planname, p.days, p.amount
                FROM clients c
                JOIN plans p ON c.plan_id = p.id
                WHERE c.end_date < CURRENT_DATE
                    AND c.end_date >= CURRENT_DATE - INTERVAL '30 days'
                    AND c.gym_id = %s
                ORDER BY c.end_date
        '''
    else:
        raise HTTPException(status_code=400, detail="Invalid status")

    database.cur.execute(query, (current_gym_id,))
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