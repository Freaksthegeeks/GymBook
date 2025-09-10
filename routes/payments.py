from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from config import database

router = APIRouter()


class PaymentModel(BaseModel):
    client_id: int
    amount: float
    paid_at: str
    note: Optional[str] = None
    method: Optional[str] = None


@router.get("/payments/")
def get_payments(client_id: Optional[int] = None):
    if client_id is not None:
        database.cur.execute(
            """
            SELECT id, client_id, amount, paid_at, note, method, created_at
            FROM payments
            WHERE client_id = %s
            ORDER BY paid_at DESC, id DESC
            """,
            (client_id,),
        )
    else:
        database.cur.execute(
            """
            SELECT id, client_id, amount, paid_at, note, method, created_at
            FROM payments
            ORDER BY paid_at DESC, id DESC
            """
        )

    rows = database.cur.fetchall()
    payments = []
    for row in rows:
        payments.append(
            {
                "id": row[0],
                "client_id": row[1],
                "amount": float(row[2]) if row[2] is not None else 0.0,
                "paid_at": str(row[3]) if row[3] else None,
                "note": row[4],
                "method": row[5],
                "created_at": str(row[6]) if row[6] else None,
            }
        )
    return {"payments": payments}


@router.post("/payments/")
def create_payment(payment: PaymentModel):
    try:
        database.cur.execute(
            """
            INSERT INTO payments (client_id, amount, paid_at, note, method)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                payment.client_id,
                payment.amount,
                payment.paid_at,
                payment.note,
                payment.method,
            ),
        )
        database.conn.commit()
        payment_id = database.cur.fetchone()[0]
        return {"id": payment_id, "message": "Payment created successfully"}
    except Exception as e:
        database.conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))


