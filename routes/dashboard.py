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

    return {
        "total_members": total,
        "active_members": active,
        "expiring_in_10_days": expiring_10,
        "expired_in_last_30_days": expired_30
    }
