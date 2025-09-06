from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config import database

router = APIRouter()


class PlanModel(BaseModel):
    planname: str
    days: int
    amount: float


@router.post("/plans/")
def create_plan(plan: PlanModel):
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


@router.get("/plans/")
def get_plans():
    database.cur.execute("SELECT id,planname,days,amount FROM plans order by id")
    rows = database.cur.fetchall()
    plans = []
    for row in rows:
        plans.append({
            "id": row[0],
            "planname": row[1],
            "days": row[2],
            "amount": float(row[3]) if row[3] else None,
        })
    return {"plans": plans}


@router.put("/plans/{plan_id}")
def update_plan(plan_id: int, plan: PlanModel):
    database.cur.execute(
        "UPDATE plans SET planname = %s, days = %s, amount = %s WHERE id = %s RETURNING id",
        (plan.planname, plan.days, plan.amount, plan_id),
    )
    database.conn.commit()
    if database.cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="plan not found")
    return {"message": "plan updated successfully"}


@router.delete("/plans/{plan_id}")
def delete_plan(plan_id: int):
    database.cur.execute("DELETE FROM plans WHERE id = %s RETURNING id", (plan_id,))
    database.conn.commit()
    if database.cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="plan not found")
    return {"message": "plan deleted successfully"}
