from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from config import database  # Import database connection
from datetime import date,timedelta
from fastapi import Query
from typing import Optional
app = FastAPI()

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
    clients = database.cur.fetchall()
    return {"clients": clients}

# ✅ Read Single client(use it as search function)
@app.get("/clients/{client_id}")
def get_client(client_id: int):
    database.cur.execute("SELECT id,clientname,phonenumber,dateofbirth,gender,bloodgroup,address,notes,email,height,weight FROM clients WHERE id = %s", (client_id,))
    client = database.cur.fetchone()
    if not client:
        raise HTTPException(status_code=404, detail="client not found")
    return {"specific client detail":client}  

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
    plans = database.cur.fetchall()
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
    staffs = database.cur.fetchall()
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
    return {"status": status, "clients": rows}

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
    leads = database.cur.fetchall()
    return {"leads": leads}

@app.delete("/leads/{lead_id}")
def delete_lead(lead_id: int):
    database.cur.execute("DELETE FROM leads WHERE id = %s RETURNING id", (lead_id,))
    database.conn.commit()
    if database.cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"message": "Lead deleted successfully"}
