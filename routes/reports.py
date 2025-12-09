from fastapi import APIRouter
from config import database
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/reports/revenue")
def get_revenue_report(period: str = "monthly"):
    """Get revenue data for charts"""
    if period == "daily":
        date_trunc = "DAY"
        interval = "7 days"
    elif period == "weekly":
        date_trunc = "WEEK"
        interval = "8 weeks"
    elif period == "yearly":
        date_trunc = "YEAR"
        interval = "5 years"
    else:  # monthly
        date_trunc = "MONTH"
        interval = "12 months"
    
    try:
        database.cur.execute(f"""
            SELECT 
                DATE_TRUNC('{date_trunc}', paid_at::date) as period,
                SUM(amount) as total_revenue
            FROM payments 
            WHERE paid_at >= CURRENT_DATE - INTERVAL '{interval}'
            GROUP BY period
            ORDER BY period
        """)
        
        rows = database.cur.fetchall()
        revenue_data = []
        for row in rows:
            try:
                period_str = row[0].strftime('%Y-%m-%d') if row[0] is not None else None
            except:
                period_str = str(row[0]) if row[0] is not None else None
            
            revenue_data.append({
                "period": period_str,
                "total_revenue": float(row[1]) if row[1] is not None else 0.0
            })
        
        return {"revenue_data": revenue_data}
    except Exception as e:
        print(f"Error in get_revenue_report: {str(e)}")
        import traceback
        traceback.print_exc()
        # Rollback transaction in case of error
        database.conn.rollback()
        return {"revenue_data": [], "error": str(e)}

@router.get("/reports/revenue-by-plan")
def get_revenue_by_plan():
    """Get revenue broken down by membership plan"""
    try:
        database.cur.execute("""
            SELECT 
                p.planname,
                COALESCE(SUM(pay.amount), 0) as total_revenue
            FROM plans p
            LEFT JOIN clients c ON p.id = c.plan_id
            LEFT JOIN payments pay ON c.id = pay.client_id
            GROUP BY p.id, p.planname
            ORDER BY total_revenue DESC
        """)
        
        rows = database.cur.fetchall()
        plan_revenue = []
        for row in rows:
            plan_revenue.append({
                "plan_name": row[0] if row[0] is not None else 'Unknown',
                "total_revenue": float(row[1]) if row[1] is not None else 0.0
            })
        
        return {"plan_revenue": plan_revenue}
    except Exception as e:
        print(f"Error in get_revenue_by_plan: {str(e)}")
        import traceback
        traceback.print_exc()
        # Rollback transaction in case of error
        database.conn.rollback()
        return {"plan_revenue": [], "error": str(e)}

@router.get("/reports/client-growth")
def get_client_growth(period: str = "monthly"):
    """Get client growth data"""
    if period == "daily":
        date_trunc = "DAY"
        interval = "30 days"
    elif period == "weekly":
        date_trunc = "WEEK"
        interval = "12 weeks"
    elif period == "yearly":
        date_trunc = "YEAR"
        interval = "5 years"
    else:  # monthly
        date_trunc = "MONTH"
        interval = "24 months"
    
    try:
        database.cur.execute(f"""
            SELECT 
                DATE_TRUNC('{date_trunc}', created_at::date) as period,
                COUNT(*) as new_clients
            FROM clients 
            WHERE created_at >= CURRENT_DATE - INTERVAL '{interval}'
            GROUP BY period
            ORDER BY period
        """)
        
        rows = database.cur.fetchall()
        growth_data = []
        for row in rows:
            try:
                period_str = row[0].strftime('%Y-%m-%d') if row[0] is not None else None
            except:
                period_str = str(row[0]) if row[0] is not None else None
            
            growth_data.append({
                "period": period_str,
                "new_clients": row[1] if row[1] is not None else 0
            })
        
        return {"growth_data": growth_data}
    except Exception as e:
        print(f"Error in get_client_growth: {str(e)}")
        import traceback
        traceback.print_exc()
        # Rollback transaction in case of error
        database.conn.rollback()
        return {"growth_data": [], "error": str(e)}

@router.get("/reports/plan-distribution")
def get_plan_distribution():
    """Get distribution of clients by plan"""
    try:
        database.cur.execute("""
            SELECT 
                p.planname,
                COUNT(c.id) as client_count
            FROM plans p
            LEFT JOIN clients c ON p.id = c.plan_id
            GROUP BY p.id, p.planname
            ORDER BY client_count DESC
        """)
        
        rows = database.cur.fetchall()
        plan_distribution = []
        for row in rows:
            plan_distribution.append({
                "plan_name": row[0] if row[0] is not None else 'Unknown',
                "client_count": row[1] if row[1] is not None else 0
            })
        
        return {"plan_distribution": plan_distribution}
    except Exception as e:
        print(f"Error in get_plan_distribution: {str(e)}")
        import traceback
        traceback.print_exc()
        # Rollback transaction in case of error
        database.conn.rollback()
        return {"plan_distribution": [], "error": str(e)}

@router.get("/reports/payment-methods")
def get_payment_methods():
    """Get payment method distribution"""
    try:
        database.cur.execute("""
            SELECT 
                method,
                COUNT(*) as count,
                SUM(amount) as total_amount
            FROM payments 
            WHERE method IS NOT NULL
            GROUP BY method
            ORDER BY total_amount DESC
        """)
        
        rows = database.cur.fetchall()
        payment_methods = []
        for row in rows:
            payment_methods.append({
                "method": row[0] if row[0] is not None else 'Unknown',
                "count": row[1] if row[1] is not None else 0,
                "total_amount": float(row[2]) if row[2] is not None else 0.0
            })
        
        return {"payment_methods": payment_methods}
    except Exception as e:
        print(f"Error in get_payment_methods: {str(e)}")
        import traceback
        traceback.print_exc()
        # Rollback transaction in case of error
        database.conn.rollback()
        return {"payment_methods": [], "error": str(e)}

@router.get("/reports/membership-status")
def get_membership_status():
    """Get membership status distribution"""
    try:
        database.cur.execute("""
            SELECT 
                CASE 
                    WHEN end_date >= CURRENT_DATE THEN 'Active'
                    WHEN end_date < CURRENT_DATE THEN 'Expired'
                    ELSE 'Other'
                END as status,
                COUNT(*) as count
            FROM clients
            GROUP BY status
            ORDER BY count DESC
        """)
        
        rows = database.cur.fetchall()
        membership_status = []
        for row in rows:
            membership_status.append({
                "status": row[0] if row[0] is not None else 'Unknown',
                "count": row[1] if row[1] is not None else 0
            })
        
        return {"membership_status": membership_status}
    except Exception as e:
        print(f"Error in get_membership_status: {str(e)}")
        import traceback
        traceback.print_exc()
        # Rollback transaction in case of error
        database.conn.rollback()
        return {"membership_status": [], "error": str(e)}

@router.get("/reports/age-distribution")
def get_age_distribution():
    """Get client age distribution"""
    try:
        database.cur.execute("""
            SELECT 
                age_group,
                count
            FROM (
                SELECT 
                    CASE 
                        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, dateofbirth::date)) < 18 THEN '<18'
                        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, dateofbirth::date)) BETWEEN 18 AND 25 THEN '18-25'
                        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, dateofbirth::date)) BETWEEN 26 AND 35 THEN '26-35'
                        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, dateofbirth::date)) BETWEEN 36 AND 45 THEN '36-45'
                        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, dateofbirth::date)) BETWEEN 46 AND 55 THEN '46-55'
                        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, dateofbirth::date)) > 55 THEN '55+'
                        ELSE 'Unknown'
                    END as age_group,
                    COUNT(*) as count
                FROM clients
                WHERE dateofbirth IS NOT NULL
                GROUP BY 
                    CASE 
                        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, dateofbirth::date)) < 18 THEN '<18'
                        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, dateofbirth::date)) BETWEEN 18 AND 25 THEN '18-25'
                        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, dateofbirth::date)) BETWEEN 26 AND 35 THEN '26-35'
                        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, dateofbirth::date)) BETWEEN 36 AND 45 THEN '36-45'
                        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, dateofbirth::date)) BETWEEN 46 AND 55 THEN '46-55'
                        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, dateofbirth::date)) > 55 THEN '55+'
                        ELSE 'Unknown'
                    END
            ) as age_data
            ORDER BY 
                CASE age_group
                    WHEN '<18' THEN 1
                    WHEN '18-25' THEN 2
                    WHEN '26-35' THEN 3
                    WHEN '36-45' THEN 4
                    WHEN '46-55' THEN 5
                    WHEN '55+' THEN 6
                    ELSE 7
                END
        """)
        
        rows = database.cur.fetchall()
        age_distribution = []
        for row in rows:
            age_distribution.append({
                "age_group": row[0] if row[0] is not None else 'Unknown',
                "count": row[1] if row[1] is not None else 0
            })
        
        return {"age_distribution": age_distribution}
    except Exception as e:
        print(f"Error in get_age_distribution: {str(e)}")
        import traceback
        traceback.print_exc()
        # Rollback transaction in case of error
        database.conn.rollback()
        return {"age_distribution": [], "error": str(e)}

@router.get("/reports/gender-distribution")
def get_gender_distribution():
    """Get client gender distribution"""
    try:
        database.cur.execute("""
            SELECT 
                gender,
                COUNT(*) as count
            FROM clients
            GROUP BY gender
            ORDER BY count DESC
        """)
        
        rows = database.cur.fetchall()
        gender_distribution = []
        for row in rows:
            gender_distribution.append({
                "gender": row[0] if row[0] is not None else 'Unknown',
                "count": row[1] if row[1] is not None else 0
            })
        
        return {"gender_distribution": gender_distribution}
    except Exception as e:
        print(f"Error in get_gender_distribution: {str(e)}")
        import traceback
        traceback.print_exc()
        # Rollback transaction in case of error
        database.conn.rollback()
        return {"gender_distribution": [], "error": str(e)}