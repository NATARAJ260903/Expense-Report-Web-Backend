from fastapi import Header, HTTPException

def create_token(user: dict) -> str:
    return f"user:{user['id']}:{user['role']}"

def parse_token(token: str) -> dict:
    try:
        prefix, user_id, role = token.split(":")
        if prefix != "user":
            raise ValueError
        return {"id": int(user_id), "role": role}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(authorization: str = Header(...)) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    return parse_token(authorization.replace("Bearer ", "", 1))
