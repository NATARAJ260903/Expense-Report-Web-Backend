from fastapi import APIRouter, Depends, HTTPException, Query
from app.db import get_connection
from app.schemas import ExpenseCreate, ExpenseUpdate, RejectRequest
from app.auth import get_current_user
from app.utils.permissions import require_role

router = APIRouter(prefix="/expenses", tags=["Expenses"])

def get_expense(cur, expense_id):
    cur.execute(
        """SELECT e.*, emp.name AS employee_name, emp.department
           FROM expenses e JOIN employees emp ON emp.id=e.employee_id
           WHERE e.id=%s""",
        (expense_id,)
    )
    return cur.fetchone()

@router.post("")
def create_expense(payload: ExpenseCreate, user=Depends(get_current_user)):
    require_role(user, ["employee"])
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute(
                """INSERT INTO expenses
                (employee_id,title,category,amount,expense_date,receipt_filename,description,status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,'draft')""",
                (user["id"],payload.title,payload.category,payload.amount,payload.expense_date,
                 payload.receipt_filename,payload.description)
            )
            return get_expense(cur, cur.lastrowid)
    finally:
        con.close()

@router.get("")
def list_expenses(employee_id: int | None = Query(default=None), user=Depends(get_current_user)):
    con = get_connection()
    try:
        with con.cursor() as cur:
            if user["role"] == "employee":
                cur.execute(
                    """SELECT e.*,emp.name AS employee_name,emp.department
                       FROM expenses e JOIN employees emp ON emp.id=e.employee_id
                       WHERE e.employee_id=%s ORDER BY e.created_at DESC""",
                    (user["id"],)
                )
            elif employee_id:
                cur.execute(
                    """SELECT e.*,emp.name AS employee_name,emp.department
                       FROM expenses e JOIN employees emp ON emp.id=e.employee_id
                       WHERE e.employee_id=%s ORDER BY e.created_at DESC""",
                    (employee_id,)
                )
            else:
                cur.execute(
                    """SELECT e.*,emp.name AS employee_name,emp.department
                       FROM expenses e JOIN employees emp ON emp.id=e.employee_id
                       ORDER BY e.created_at DESC"""
                )
            return cur.fetchall()
    finally:
        con.close()

@router.get("/{expense_id}")
def get_one(expense_id: int, user=Depends(get_current_user)):
    con = get_connection()
    try:
        with con.cursor() as cur:
            expense = get_expense(cur, expense_id)
            if not expense:
                raise HTTPException(status_code=404, detail="Expense not found")
            if user["role"] == "employee" and expense["employee_id"] != user["id"]:
                raise HTTPException(status_code=403, detail="Access denied")
            return expense
    finally:
        con.close()

@router.put("/{expense_id}")
def update_expense(expense_id: int, payload: ExpenseUpdate, user=Depends(get_current_user)):
    require_role(user, ["employee"])
    con = get_connection()
    try:
        with con.cursor() as cur:
            expense = get_expense(cur, expense_id)
            if not expense:
                raise HTTPException(status_code=404, detail="Expense not found")
            if expense["employee_id"] != user["id"]:
                raise HTTPException(status_code=403, detail="You can edit only your own expenses")
            if expense["status"] not in ("draft","rejected"):
                raise HTTPException(status_code=409, detail="Only draft or rejected expenses are editable")
            cur.execute(
                """UPDATE expenses SET title=%s,category=%s,amount=%s,expense_date=%s,
                   receipt_filename=%s,description=%s,status='draft',submitted_at=NULL WHERE id=%s""",
                (payload.title,payload.category,payload.amount,payload.expense_date,
                 payload.receipt_filename,payload.description,expense_id)
            )
            return get_expense(cur, expense_id)
    finally:
        con.close()

@router.post("/{expense_id}/submit")
def submit_expense(expense_id: int, user=Depends(get_current_user)):
    require_role(user, ["employee"])
    con = get_connection()
    try:
        with con.cursor() as cur:
            expense = get_expense(cur, expense_id)
            if not expense:
                raise HTTPException(status_code=404, detail="Expense not found")
            if expense["employee_id"] != user["id"]:
                raise HTTPException(status_code=403, detail="You can submit only your own expenses")
            if expense["status"] not in ("draft","rejected"):
                raise HTTPException(status_code=409, detail="Expense cannot be submitted from current status")
            cur.execute("UPDATE expenses SET status='submitted',submitted_at=NOW() WHERE id=%s",(expense_id,))
            return get_expense(cur, expense_id)
    finally:
        con.close()

@router.delete("/{expense_id}")
def delete_expense(expense_id: int, user=Depends(get_current_user)):
    require_role(user, ["employee"])
    con = get_connection()
    try:
        with con.cursor() as cur:
            expense = get_expense(cur, expense_id)
            if not expense:
                raise HTTPException(status_code=404, detail="Expense not found")
            if expense["employee_id"] != user["id"]:
                raise HTTPException(status_code=403, detail="You can delete only your own expenses")
            if expense["status"] != "draft":
                raise HTTPException(status_code=409, detail="Only draft expenses can be deleted")
            cur.execute("DELETE FROM expenses WHERE id=%s",(expense_id,))
            return {"message":"Expense deleted"}
    finally:
        con.close()

@router.post("/{expense_id}/approve")
def approve_expense(expense_id: int, user=Depends(get_current_user)):
    require_role(user, ["manager"])
    con = get_connection()
    try:
        with con.cursor() as cur:
            expense = get_expense(cur, expense_id)
            if not expense:
                raise HTTPException(status_code=404, detail="Expense not found")
            cur.execute("SELECT manager_id FROM employees WHERE id=%s",(expense["employee_id"],))
            owner = cur.fetchone()
            if not owner or owner["manager_id"] != user["id"]:
                raise HTTPException(status_code=403, detail="Expense is not from your team")
            if expense["status"] != "submitted":
                raise HTTPException(status_code=409, detail="Only submitted expenses can be approved")
            cur.execute("UPDATE expenses SET status='approved' WHERE id=%s",(expense_id,))
            cur.execute(
                "INSERT INTO approvals (expense_id,actioned_by,action,comment) VALUES (%s,%s,'approved',%s)",
                (expense_id,user["id"],"Approved")
            )
            return get_expense(cur, expense_id)
    finally:
        con.close()

@router.post("/{expense_id}/reject")
def reject_expense(expense_id: int, payload: RejectRequest, user=Depends(get_current_user)):
    require_role(user, ["manager"])
    con = get_connection()
    try:
        with con.cursor() as cur:
            expense = get_expense(cur, expense_id)
            if not expense:
                raise HTTPException(status_code=404, detail="Expense not found")
            cur.execute("SELECT manager_id FROM employees WHERE id=%s",(expense["employee_id"],))
            owner = cur.fetchone()
            if not owner or owner["manager_id"] != user["id"]:
                raise HTTPException(status_code=403, detail="Expense is not from your team")
            if expense["status"] != "submitted":
                raise HTTPException(status_code=409, detail="Only submitted expenses can be rejected")
            cur.execute("UPDATE expenses SET status='rejected' WHERE id=%s",(expense_id,))
            cur.execute(
                "INSERT INTO approvals (expense_id,actioned_by,action,comment) VALUES (%s,%s,'rejected',%s)",
                (expense_id,user["id"],payload.comment)
            )
            return get_expense(cur, expense_id)
    finally:
        con.close()

@router.post("/{expense_id}/mark-paid")
def mark_paid(expense_id: int, user=Depends(get_current_user)):
    require_role(user, ["finance_admin"])
    con = get_connection()
    try:
        with con.cursor() as cur:
            expense = get_expense(cur, expense_id)
            if not expense:
                raise HTTPException(status_code=404, detail="Expense not found")
            if expense["status"] != "approved":
                raise HTTPException(status_code=409, detail="Only approved expenses can be marked paid")
            cur.execute("UPDATE expenses SET status='paid' WHERE id=%s",(expense_id,))
            cur.execute(
                "INSERT INTO approvals (expense_id,actioned_by,action,comment) VALUES (%s,%s,'paid',%s)",
                (expense_id,user["id"],"Payment processed")
            )
            return get_expense(cur, expense_id)
    finally:
        con.close()
