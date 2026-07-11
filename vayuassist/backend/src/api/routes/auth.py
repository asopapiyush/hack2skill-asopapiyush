from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.models.models import User
from src.services.auth_service import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    Token
)
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str = ""

class UserLogin(BaseModel):
    email: str
    password: str

def get_token_from_request(request: Request, token: str = None) -> str:
    if token:
        return token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    return None

@router.post("/register", response_model=Token)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create token
    access_token = create_access_token(data={"sub": new_user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": new_user.id
    }

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    # Find user
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="User is inactive")
    
    # Create token
    access_token = create_access_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id
    }

@router.get("/me")
async def get_current_user(request: Request, token: str = None, db: Session = Depends(get_db)):
    extracted_token = get_token_from_request(request, token)
    print(f"DEBUG: Headers: {dict(request.headers)}")
    print(f"DEBUG: Query Token: {token}")
    print(f"DEBUG: Extracted Token: {extracted_token}")
    if not extracted_token:
        print("DEBUG: Extracted token is None")
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    from src.services.auth_service import decode_token
    user_id = decode_token(extracted_token)
    print(f"DEBUG: Decoded User ID: {user_id}")
    
    if not user_id:
        print("DEBUG: Decoded user_id is None")
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == user_id).first()
    print(f"DEBUG: Database User: {user}")
    if not user:
        print("DEBUG: User not found in DB")
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "family_size": user.family_size,
        "location": user.location,
        "region": user.region
    }

@router.put("/profile")
async def update_profile(
    profile_data: dict,
    request: Request,
    token: str = None,
    db: Session = Depends(get_db)
):
    extracted_token = get_token_from_request(request, token)
    if not extracted_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    from src.services.auth_service import decode_token
    user_id = decode_token(extracted_token)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update allowed fields
    if "family_size" in profile_data:
        user.family_size = str(profile_data["family_size"])
    if "location" in profile_data:
        user.location = profile_data["location"]
    if "region" in profile_data:
        user.region = profile_data["region"]
    if "health_conditions" in profile_data:
        user.health_conditions = str(profile_data["health_conditions"])
    
    db.commit()
    db.refresh(user)
    
    return {"message": "Profile updated", "user_id": user.id}
