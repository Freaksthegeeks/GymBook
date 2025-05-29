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



# ✅ Create client (add page)
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