# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException
from models import SignupRequest, LoginRequest
from database import users_collection
# pyrefly: ignore [missing-import]
from auth.security import hash_password, verify_password
# pyrefly: ignore [missing-import]
from auth.jwt_handler import create_access_token
router = APIRouter()






@router.post("/signup")
def signup(req: SignupRequest):

    existing = users_collection.find_one({
        "email": req.email
    })

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    users_collection.insert_one({
        "username": req.username,
        "email": req.email,
        "password": hash_password(req.password)
    })

    return {
        "message": "Account created successfully"
    }



@router.post("/login")
def login(req: LoginRequest):

    user = users_collection.find_one({
        "email": req.email
    })

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(req.password, user["password"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token({
        "user_id": str(user["_id"])
    })

    return {
        "access_token": token,
        "username": user["username"]
    }