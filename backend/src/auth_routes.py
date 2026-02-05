"""Authentication routes for user management."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List

from src.database import get_db
from src.auth import (
    authenticate_user,
    create_user,
    create_access_token,
    get_current_user,
    get_user_api_key,
    save_user_api_key,
    delete_user_api_key
)
from src.models_db import User, APIKey

router = APIRouter(prefix="/api/auth", tags=["authentication"])


# Pydantic models
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_admin: bool
    
    class Config:
        from_attributes = True


class APIKeyCreate(BaseModel):
    provider: str  # openai, gemini, anthropic, perplexity
    api_key: str


class APIKeyResponse(BaseModel):
    provider: str
    created_at: str
    
    class Config:
        from_attributes = True


@router.post("/register", response_model=Token)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user
    user = create_user(db, user_data.email, user_data.username, user_data.password)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_admin": user.is_admin
        }
    }


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token."""
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_admin": user.is_admin
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@router.post("/api-keys", response_model=APIKeyResponse)
async def add_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add or update an API key for the current user."""
    valid_providers = ["openai", "gemini", "anthropic", "perplexity"]
    if key_data.provider not in valid_providers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid provider. Must be one of: {', '.join(valid_providers)}"
        )
    
    api_key = save_user_api_key(db, current_user.id, key_data.provider, key_data.api_key)
    
    return {
        "provider": api_key.provider,
        "created_at": api_key.created_at.isoformat()
    }


@router.get("/api-keys", response_model=List[APIKeyResponse])
async def get_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all API keys for the current user (without showing the actual keys)."""
    keys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()
    return [
        {
            "provider": key.provider,
            "created_at": key.created_at.isoformat()
        }
        for key in keys
    ]


@router.delete("/api-keys/{provider}")
async def delete_api_key(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an API key for the current user."""
    success = delete_user_api_key(db, current_user.id, provider)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    return {"message": f"API key for {provider} deleted successfully"}
