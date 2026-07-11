from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from pydantic import BaseModel
import os

# JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-min-32-chars-long!!")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str

class TokenData(BaseModel):
    user_id: Optional[str] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a bcrypt-hashed password.
    
    Args:
        plain_password: The raw password to check.
        hashed_password: The bcrypt-hashed password.
        
    Returns:
        bool: True if password matches, False otherwise.
    """
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """
    Generate a bcrypt hash of a password.
    
    Args:
        password: The plain text password.
        
    Returns:
        str: The hashed password.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new JWT access token.
    
    Args:
        data: Dict payload containing sub (user ID).
        expires_delta: Optional duration for token expiry.
        
    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[str]:
    """
    Decode a JWT token to extract the user ID (sub).
    
    Args:
        token: The encoded JWT token.
        
    Returns:
        Optional[str]: The user ID if valid, None otherwise.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None
