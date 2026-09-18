from fastapi import APIRouter, Depends, Query
from app.db import get_connection
from app.auth import get_current_user
from app.utils.permissions import require_role

router = APIRouter(prefix="/finance", tags=["Finance"])

@router.get("/expenses")
def finance_expenses(
    department: str | None = Query(default=None),
    category: str | None = Query(default=None),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    user=Depends(get_current_user)
):
    require_role(user, ["finance_admin"])
    con = get_connection()
    try:
        with con.cursor() as cur:
            query = """SELECT e.*,emp.name AS employee_name,emp.department
                       FROM expenses e JOIN employees emp ON emp.id=e.employee_id
                       WHERE e.status='approved'"""
            params = []
            if department:
                query += " AND emp.department=%s"; params.append(department)
            if category:
                query += " AND e.category=%s"; params.append(category)
            if start_date:
                query += " AND e.expense_date >= %s"; params.append(start_date)
            if end_date:
                query += " AND e.expense_date <= %s"; params.append(end_date)
            query += " ORDER BY e.created_at DESC"
            cur.execute(query, params)
            return cur.fetchall()
    finally:
        con.close()

@router.get("/summary")
def finance_summary(user=Depends(get_current_user)):
    require_role(user, ["finance_admin"])
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute(
                """SELECT
                   COALESCE(SUM(CASE WHEN status='submitted' THEN amount ELSE 0 END),0) AS total_submitted,
                   COALESCE(SUM(CASE WHEN status='approved' THEN amount ELSE 0 END),0) AS total_approved,
                   COALESCE(SUM(CASE WHEN status='paid' THEN amount ELSE 0 END),0) AS total_paid
                   FROM expenses"""
            )
            totals = cur.fetchone()
            cur.execute(
                """SELECT category,COALESCE(SUM(amount),0) AS total
                   FROM expenses WHERE status IN ('approved','paid')
                   GROUP BY category ORDER BY total DESC"""
            )
            by_category = cur.fetchall()
            cur.execute(
                """SELECT emp.department,COALESCE(SUM(e.amount),0) AS total
                   FROM expenses e JOIN employees emp ON emp.id=e.employee_id
                   WHERE e.status IN ('approved','paid')
                   GROUP BY emp.department ORDER BY total DESC"""
            )
            by_department = cur.fetchall()
            return {"totals":totals,"by_category":by_category,"by_department":by_department}
    finally:
        con.close()
