# auth.py - JWT utilities, password hashing, and FastAPI authentication dependencies

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel
from .config import settings
from .models import User
from .db import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


# --- SCHEMAS ---


# PUBLIC_INTERFACE
class Token(BaseModel):
    """Bearer token returned to client."""
    access_token: str
    token_type: str


# PUBLIC_INTERFACE
class TokenData(BaseModel):
    """JWT token payload structure."""
    username: Optional[str] = None


# PUBLIC_INTERFACE
class UserCreateSchema(BaseModel):
    """Request schema for registering a user."""
    username: str
    password: str


# PUBLIC_INTERFACE
class UserSchema(BaseModel):
    """Response schema for returning user info."""
    id: int
    username: str
    created_at: datetime

    class Config:
        orm_mode = True


# --- PASSWORD UTILS ---


# PUBLIC_INTERFACE
def verify_password(plain_password, hashed_password):
    """Verify a (plain) password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


# PUBLIC_INTERFACE
def get_password_hash(password):
    """Hash a cleartext password."""
    return pwd_context.hash(password)


# --- JWT UTILS ---


# PUBLIC_INTERFACE
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a new JWT for the given user data."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


# PUBLIC_INTERFACE
def decode_access_token(token: str) -> Optional[TokenData]:
    """Decode JWT and validate payload."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        username: str = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except JWTError:
        return None


# PUBLIC_INTERFACE
def authenticate_user(db: Session, username: str, password: str):
    """Verify user credentials and return user if valid."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


# PUBLIC_INTERFACE
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency that gets current user or raises 401."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = decode_access_token(token)
    if not token_data or not token_data.username:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if not user:
        raise credentials_exception
    return user
