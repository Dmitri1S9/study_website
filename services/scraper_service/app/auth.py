from fastapi import Header, HTTPException

async def verify_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if authorization != "Bearer secret_token_123":
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    return {"user": "test_user"}
