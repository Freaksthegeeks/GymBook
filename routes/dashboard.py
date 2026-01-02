from fastapi import APIRouter
from config import database
from fastapi import Depends
from index import get_current_user, get_current_gym_id

router = APIRouter()


@router.get("/dashboard/stats")
def dashboard_stats(current_gym_id: int = Depends(get_current_gym_id)):
    database.cur.execute("SELECT COUNT(*) FROM clients WHERE gym_id = %s", (current_gym_id,))
    total = database.cur.fetchone()[0]

    database.cur.execute("SELECT COUNT(*) FROM clients WHERE end_date >= CURRENT_DATE AND gym_id = %s", (current_gym_id,))
    active = database.cur.fetchone()[0]

    database.cur.execute("SELECT COUNT(*) FROM clients WHERE end_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '10 days' AND gym_id = %s", (current_gym_id,))
    expiring_10 = database.cur.fetchone()[0]

    database.cur.execute("SELECT COUNT(*) FROM clients WHERE end_date < CURRENT_DATE AND end_date >= CURRENT_DATE - INTERVAL '30 days' AND gym_id = %s", (current_gym_id,))
    expired_30 = database.cur.fetchone()[0]

    database.cur.execute("""
        SELECT COUNT(*) 
        FROM clients 
        WHERE EXTRACT(MONTH FROM dateofbirth::date) = EXTRACT(MONTH FROM CURRENT_DATE)
          AND EXTRACT(DAY FROM dateofbirth::date) = EXTRACT(DAY FROM CURRENT_DATE)
          AND gym_id = %s
    """, (current_gym_id,))
    birthdays_today = database.cur.fetchone()[0]

    # Get lead count
    database.cur.execute("SELECT COUNT(*) FROM leads WHERE gym_id = %s", (current_gym_id,))
    total_leads = database.cur.fetchone()[0]

    return {
        "total_members": total,
        "active_members": active,
        "expiring_in_10_days": expiring_10,
        "expired_in_last_30_days": expired_30,
        "birthdays_today": birthdays_today,
        "total_leads": total_leads
    }


@router.get("/dashboard/due_members")
def get_due_members(current_gym_id: int = Depends(get_current_gym_id)):
    """Get clients with pending payments (positive balance_due)"""
    database.cur.execute("""
        SELECT c.id, c.clientname, c.phonenumber, c.balance_due
        FROM clients c
        WHERE c.balance_due > 0 AND c.gym_id = %s
        ORDER BY c.balance_due DESC
    """, (current_gym_id,))
    rows = database.cur.fetchall()
    due_members = []
    for row in rows:
        due_members.append({
            "id": row[0],
            "clientname": row[1],
            "phonenumber": str(row[2]),
            "balance_due": float(row[3]) if row[3] else 0.0
        })
    return {"due_members": due_members}