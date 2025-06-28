from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .db import get_db, init_db
from .models import User
from .auth import (
    UserCreateSchema,
    UserSchema,
    Token,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
)

app = FastAPI(
    title="Tic Tac Toe Backend API",
    description="Handles user, game, and authentication logic for Tic Tac Toe.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Ensure tables are created when server starts (idempotent)
@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def health_check():
    """Health check endpoint for the Tic Tac Toe backend."""
    return {"message": "Healthy"}


# --- User Registration ---
# PUBLIC_INTERFACE
@app.post(
    "/users/register",
    response_model=UserSchema,
    tags=["users"],
    summary="Register a new user",
    description="Registers a new user and returns user details.",
)
def register(
    user_create: UserCreateSchema,
    db: Session = Depends(get_db),
):
    """Registers a new user after checking username availability."""
    db_user = db.query(User).filter(User.username == user_create.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists.")
    user = User(
        username=user_create.username,
        password_hash=get_password_hash(user_create.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# --- User Login (JWT token) ---
# PUBLIC_INTERFACE
@app.post(
    "/users/login",
    response_model=Token,
    tags=["users"],
    summary="User login",
    description="Authenticate user and get JWT token.",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authenticates the user and issues JWT access token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# --- Get Current User (for session-based APIs) ---
# PUBLIC_INTERFACE
@app.get(
    "/users/me",
    response_model=UserSchema,
    tags=["users"],
    summary="Get current user info",
    description="Fetches user info for the authenticated token.",
)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the currently authenticated user's profile."""
    return current_user
