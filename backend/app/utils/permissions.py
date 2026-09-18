from fastapi import HTTPException

def require_role(user: dict, allowed_roles: list[str]):
    if user["role"] not in allowed_roles:
        raise HTTPException(status_code=403, detail="Access denied")
