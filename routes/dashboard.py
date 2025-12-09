from fastapi import APIRouter
from config import database

router = APIRouter()


@router.get("/dashboard/stats")
def dashboard_stats():
    database.cur.execute("SELECT COUNT(*) FROM clients")
    total = database.cur.fetchone()[0]

    database.cur.execute("SELECT COUNT(*) FROM clients WHERE end_date >= CURRENT_DATE")
    active = database.cur.fetchone()[0]

    database.cur.execute("SELECT COUNT(*) FROM clients WHERE end_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '10 days'")
    expiring_10 = database.cur.fetchone()[0]

    database.cur.execute("SELECT COUNT(*) FROM clients WHERE end_date < CURRENT_DATE AND end_date >= CURRENT_DATE - INTERVAL '30 days'")
    expired_30 = database.cur.fetchone()[0]

    database.cur.execute("""
        SELECT COUNT(*) 
        FROM clients 
        WHERE EXTRACT(MONTH FROM dateofbirth::date) = EXTRACT(MONTH FROM CURRENT_DATE)
          AND EXTRACT(DAY FROM dateofbirth::date) = EXTRACT(DAY FROM CURRENT_DATE)
    """)
    birthdays_today = database.cur.fetchone()[0]

    # Get lead count
    database.cur.execute("SELECT COUNT(*) FROM leads")
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
def get_due_members():
    """Get clients with pending payments (positive balance_due)"""
    database.cur.execute("""
        SELECT c.id, c.clientname, c.phonenumber, c.balance_due
        FROM clients c
        WHERE c.balance_due > 0
        ORDER BY c.balance_due DESC
    """)
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