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
        # First, get the client's plan amount
        database.cur.execute("""
            SELECT p.amount, c.total_paid, c.balance_due
            FROM clients c
            JOIN plans p ON c.plan_id = p.id
            WHERE c.id = %s
        """, (payment.client_id,))
        
        client_data = database.cur.fetchone()
        if not client_data:
            raise HTTPException(status_code=400, detail="Invalid client ID")
            
        plan_amount = float(client_data[0]) if client_data[0] else 0.0
        current_paid = float(client_data[1]) if client_data[1] else 0.0
        current_due = float(client_data[2]) if client_data[2] else plan_amount
        
        # Validate payment amount (allow partial payments but warn if overpaying)
        if payment.amount <= 0:
            raise HTTPException(status_code=400, detail="Payment amount must be greater than zero")
        
        # Calculate new totals
        new_paid = current_paid + payment.amount
        new_balance = plan_amount - new_paid
        
        # Insert payment record
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
        
        # Get the payment ID before doing other operations
        payment_id = database.cur.fetchone()[0]
        
        # Update client's payment status
        database.cur.execute(
            """
            UPDATE clients 
            SET total_paid = %s, balance_due = %s
            WHERE id = %s
            """,
            (new_paid, new_balance, payment.client_id)
        )
        
        database.conn.commit()
        return {
            "id": payment_id, 
            "message": "Payment created successfully",
            "balance_due": new_balance,
            "total_paid": new_paid,
            "plan_amount": plan_amount,
            "overpayment": new_balance < 0
        }
    except Exception as e:
        database.conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/payments/{payment_id}")
def update_payment(payment_id: int, payment: PaymentModel):
    try:
        # Get the original payment amount
        database.cur.execute(
            "SELECT client_id, amount FROM payments WHERE id = %s",
            (payment_id,)
        )
        original_payment = database.cur.fetchone()
        if not original_payment:
            raise HTTPException(status_code=404, detail="Payment not found")
            
        original_client_id = original_payment[0]
        original_amount = float(original_payment[1])
        
        # Get client's plan amount and current payment status
        database.cur.execute("""
            SELECT p.amount, c.total_paid, c.balance_due
            FROM clients c
            JOIN plans p ON c.plan_id = p.id
            WHERE c.id = %s
        """, (original_client_id,))
        
        client_data = database.cur.fetchone()
        if not client_data:
            raise HTTPException(status_code=400, detail="Invalid client ID")
            
        plan_amount = float(client_data[0]) if client_data[0] else 0.0
        current_paid = float(client_data[1]) if client_data[1] else 0.0
        
        # Validate payment amount
        if payment.amount <= 0:
            raise HTTPException(status_code=400, detail="Payment amount must be greater than zero")
        
        # Calculate adjusted totals
        # Remove original payment and add new payment
        adjusted_paid = current_paid - original_amount + payment.amount
        new_balance = plan_amount - adjusted_paid
        
        # Update payment record
        database.cur.execute(
            """
            UPDATE payments 
            SET client_id = %s, amount = %s, paid_at = %s, note = %s, method = %s
            WHERE id = %s
            """,
            (
                payment.client_id,
                payment.amount,
                payment.paid_at,
                payment.note,
                payment.method,
                payment_id
            ),
        )
        
        # Update client's payment status
        database.cur.execute(
            """
            UPDATE clients 
            SET total_paid = %s, balance_due = %s
            WHERE id = %s
            """,
            (adjusted_paid, new_balance, payment.client_id)
        )
        
        database.conn.commit()
        return {
            "message": "Payment updated successfully",
            "balance_due": new_balance,
            "total_paid": adjusted_paid,
            "plan_amount": plan_amount,
            "overpayment": new_balance < 0
        }
    except Exception as e:
        database.conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/payments/{payment_id}")
def delete_payment(payment_id: int):
    try:
        # Get the payment details
        database.cur.execute(
            "SELECT client_id, amount FROM payments WHERE id = %s",
            (payment_id,)
        )
        payment = database.cur.fetchone()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
            
        client_id = payment[0]
        amount = float(payment[1])
        
        # Get client's plan amount and current payment status
        database.cur.execute("""
            SELECT p.amount, c.total_paid, c.balance_due
            FROM clients c
            JOIN plans p ON c.plan_id = p.id
            WHERE c.id = %s
        """, (client_id,))
        
        client_data = database.cur.fetchone()
        if not client_data:
            raise HTTPException(status_code=400, detail="Invalid client ID")
            
        plan_amount = float(client_data[0]) if client_data[0] else 0.0
        current_paid = float(client_data[1]) if client_data[1] else 0.0
        
        # Calculate new totals after removing payment
        new_paid = current_paid - amount
        new_balance = plan_amount - new_paid
        
        # Delete payment record
        database.cur.execute(
            "DELETE FROM payments WHERE id = %s",
            (payment_id,)
        )
        
        # Update client's payment status
        database.cur.execute(
            """
            UPDATE clients 
            SET total_paid = %s, balance_due = %s
            WHERE id = %s
            """,
            (new_paid, new_balance, client_id)
        )
        
        database.conn.commit()
        return {
            "message": "Payment deleted successfully",
            "balance_due": new_balance,
            "total_paid": new_paid,
            "plan_amount": plan_amount,
            "overpayment": new_balance < 0
        }
    except Exception as e:
        database.conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))