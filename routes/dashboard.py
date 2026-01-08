from fastapi import APIRouter
from config import database
from fastapi import Depends
from index import get_current_user, get_current_gym_id

router = APIRouter()


@router.get("/dashboard/stats")
def dashboard_stats(current_gym_id: int = Depends(get_current_gym_id)):
    try:
        database.cur.execute("SELECT COUNT(*) FROM clients WHERE gym_id = %s", (current_gym_id,))
        total_row = database.cur.fetchone()
        total = total_row[0] if total_row else 0

        database.cur.execute("SELECT COUNT(*) FROM clients WHERE end_date >= CURRENT_DATE AND gym_id = %s", (current_gym_id,))
        active_row = database.cur.fetchone()
        active = active_row[0] if active_row else 0

        database.cur.execute("SELECT COUNT(*) FROM clients WHERE end_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '10 days' AND gym_id = %s", (current_gym_id,))
        expiring_10_row = database.cur.fetchone()
        expiring_10 = expiring_10_row[0] if expiring_10_row else 0

        database.cur.execute("SELECT COUNT(*) FROM clients WHERE end_date < CURRENT_DATE AND end_date >= CURRENT_DATE - INTERVAL '30 days' AND gym_id = %s", (current_gym_id,))
        expired_30_row = database.cur.fetchone()
        expired_30 = expired_30_row[0] if expired_30_row else 0

        database.cur.execute("""
            SELECT COUNT(*) 
            FROM clients 
            WHERE EXTRACT(MONTH FROM dateofbirth::date) = EXTRACT(MONTH FROM CURRENT_DATE)
              AND EXTRACT(DAY FROM dateofbirth::date) = EXTRACT(DAY FROM CURRENT_DATE)
              AND gym_id = %s
        """, (current_gym_id,))
        birthdays_row = database.cur.fetchone()
        birthdays_today = birthdays_row[0] if birthdays_row else 0

        # Get lead count
        database.cur.execute("SELECT COUNT(*) FROM leads WHERE gym_id = %s", (current_gym_id,))
        leads_row = database.cur.fetchone()
        total_leads = leads_row[0] if leads_row else 0

        return {
            "total_members": total,
            "active_members": active,
            "expiring_in_10_days": expiring_10,
            "expired_in_last_30_days": expired_30,
            "birthdays_today": birthdays_today,
            "total_leads": total_leads
        }
    except Exception as e:
        print(f"Error in dashboard_stats: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "total_members": 0,
            "active_members": 0,
            "expiring_in_10_days": 0,
            "expired_in_last_30_days": 0,
            "birthdays_today": 0,
            "total_leads": 0
        }


@router.get("/dashboard/due_members")
def get_due_members(current_gym_id: int = Depends(get_current_gym_id)):
    """Get clients with pending payments (positive balance_due)"""
    try:
        database.cur.execute("""
            SELECT c.id, c.clientname, c.phonenumber, c.balance_due
            FROM clients c
            WHERE c.balance_due > 0 AND c.gym_id = %s
            ORDER BY c.balance_due DESC
        """, (current_gym_id,))
        rows = database.cur.fetchall() if database.cur.rowcount != -1 else []
        due_members = []
        for row in rows:
            due_members.append({
                "id": row[0],
                "clientname": row[1],
                "phonenumber": str(row[2]) if row[2] else "",
                "balance_due": float(row[3]) if row[3] is not None and str(row[3]).replace('.', '').replace('-', '').isdigit() else 0.0
            })
        return {"due_members": due_members}
    except Exception as e:
        print(f"Error in get_due_members: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"due_members": []}