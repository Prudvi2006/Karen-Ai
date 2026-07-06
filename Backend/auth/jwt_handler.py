from jose import JWTError
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "963693"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
from jose import JWTError, jwt

def verify_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        print("Decoded payload:", payload)   # <-- Add this

        return payload

    except JWTError as e:
        print("JWT ERROR:", e)               # <-- Add this
        return None