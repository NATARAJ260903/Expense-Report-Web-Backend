from fastapi import APIRouter, Depends, HTTPException
from app.db import get_connection
from app.schemas import LoginRequest
from app.auth import create_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

DEMO_PASSWORDS = {
    "amit@beeja.com": "employee123",
    "priya@beeja.com": "manager123",
    "karan@beeja.com": "finance123",
}

@router.post("/login")
def login(payload: LoginRequest):
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute(
                """SELECT id,name,email,role,department,manager_id
                   FROM employees WHERE email=%s AND role=%s""",
                (payload.email, payload.role)
            )
            user = cur.fetchone()
    finally:
        con.close()
    if not user or DEMO_PASSWORDS.get(payload.email.lower()) != payload.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": create_token(user), "user": user}

@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute(
                """SELECT id,name,email,role,department,manager_id
                   FROM employees WHERE id=%s""",
                (current_user["id"],)
            )
            user = cur.fetchone()
    finally:
        con.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
