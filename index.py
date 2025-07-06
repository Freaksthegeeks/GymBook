from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from config import database  # Import database connection

app = FastAPI()

# ✅ client Model (Request Body)
class client(BaseModel):
    clientname: str
    phonenumber: str
    dateofbirth: str
    gender: str
    bloodgroup: str
    address: str
    notes: str
    email: str
    height: float
    weight: float

#CLIENTS

# ✅ Create client (add client page)
@app.post("/clients/")
def create_client(client: client):
    try:
        database.cur.execute(
            "INSERT INTO clients (clientname,phonenumber,dateofbirth,gender,bloodgroup,address,notes,email,height,weight) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
            (client.clientname, client.phonenumber, client.dateofbirth, client.gender, client.bloodgroup, client.address, client.notes, client.email, client.height, client.weight),
        )
        database.conn.commit()
        client_id = database.cur.fetchone()[0]
        return {"id": client_id, "message": "client created successfully"}
    except Exception as e:
        database.conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# ✅ Read All clients(total members)
@app.get("/clients/")
def get_clients():
    database.cur.execute("SELECT id,clientname,phonenumber,dateofbirth,gender,bloodgroup,address,notes,email,height,weight FROM clients")
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
    database.cur.execute(
        "UPDATE clients SET clientname = %s,phonenumber = %s,dateofbirth = %s,gender = %s,bloodgroup = %s,address = %s,notes = %s,email = %s,height = %s,weight = %s WHERE id = %s RETURNING id",
        (client.clientname, client.phonenumber, client.dateofbirth, client.gender, client.bloodgroup, client.address, client.notes, client.email, client.height, client.weight,client_id),
    )
    database.conn.commit()
    if database.cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="client not found")
    return {"message": "client updated successfully"}

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
    database.cur.execute("SELECT id,planname,days,amount FROM plans")
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

#staffs

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