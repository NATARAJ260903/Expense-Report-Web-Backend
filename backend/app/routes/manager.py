from fastapi import APIRouter, Depends
from app.db import get_connection
from app.auth import get_current_user
from app.utils.permissions import require_role

router = APIRouter(prefix="/manager", tags=["Manager"])

@router.get("/expenses")
def manager_expenses(user=Depends(get_current_user)):
    require_role(user, ["manager"])
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute(
                """SELECT e.*,emp.name AS employee_name,emp.department
                   FROM expenses e JOIN employees emp ON emp.id=e.employee_id
                   WHERE emp.manager_id=%s AND e.status='submitted'
                   ORDER BY e.created_at DESC""",
                (user["id"],)
            )
            return cur.fetchall()
    finally:
        con.close()

@router.get("/team-summary")
def team_summary(user=Depends(get_current_user)):
    require_role(user, ["manager"])
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute(
                """SELECT emp.department,e.status,COUNT(*) AS count,COALESCE(SUM(e.amount),0) AS total
                   FROM expenses e JOIN employees emp ON emp.id=e.employee_id
                   WHERE emp.manager_id=%s
                   GROUP BY emp.department,e.status ORDER BY emp.department,e.status""",
                (user["id"],)
            )
            return cur.fetchall()
    finally:
        con.close()
