# backend/auth_routes.py
# Create this new file in your backend folder

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

router = APIRouter(prefix="/auth", tags=["authentication"])

# Pydantic models for request/response
class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    
    @validator('email')
    def validate_chargebee_email(cls, v):
        if not v.endswith('@chargebee.com'):
            raise ValueError('Only @chargebee.com email addresses are allowed')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
    @validator('email')
    def validate_chargebee_email(cls, v):
        if not v.endswith('@chargebee.com'):
            raise ValueError('Only @chargebee.com email addresses are allowed')
        return v

class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[dict] = None
    session: Optional[dict] = None

@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignUpRequest):
    """Create a new user account (Chargebee employees only)"""
    try:
        # Create user with Supabase Auth
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "full_name": request.full_name
                }
            }
        })
        
        if response.user:
            return AuthResponse(
                success=True,
                message="Account created successfully! Please check your email for verification.",
                user={
                    "id": response.user.id,
                    "email": response.user.email,
                    "full_name": request.full_name
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create account"
            )
            
    except Exception as e:
        # Check if email already exists
        if "User already registered" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login with email and password"""
    try:
        # Sign in with Supabase Auth
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if response.user and response.session:
            # Get user profile
            profile = supabase.table("profiles")\
                .select("*")\
                .eq("id", response.user.id)\
                .single()\
                .execute()
            
            return AuthResponse(
                success=True,
                message="Login successful!",
                user={
                    "id": response.user.id,
                    "email": response.user.email,
                    "full_name": profile.data.get("full_name") if profile.data else None,
                    "role": profile.data.get("role", "Risk Analyst") if profile.data else "Risk Analyst"
                },
                session={
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_at": response.session.expires_at
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
            
    except Exception as e:
        if "Invalid login credentials" in str(e):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

@router.post("/logout")
async def logout(access_token: str):
    """Logout user"""
    try:
        # Sign out with Supabase
        response = supabase.auth.sign_out()
        
        return AuthResponse(
            success=True,
            message="Logged out successfully!"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/me")
async def get_current_user(authorization: str):
    """Get current user information"""
    try:
        # Extract token from Bearer authorization
        token = authorization.replace("Bearer ", "")
        
        # Get user from token
        response = supabase.auth.get_user(token)
        
        if response.user:
            # Get user profile
            profile = supabase.table("profiles")\
                .select("*")\
                .eq("id", response.user.id)\
                .single()\
                .execute()
            
            return AuthResponse(
                success=True,
                message="User retrieved successfully",
                user={
                    "id": response.user.id,
                    "email": response.user.email,
                    "full_name": profile.data.get("full_name") if profile.data else None,
                    "role": profile.data.get("role", "Risk Analyst") if profile.data else "Risk Analyst"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.post("/verify-email")
async def verify_email(email: EmailStr):
    """Check if email is valid Chargebee email"""
    if email.endswith('@chargebee.com'):
        # Check if email already exists
        try:
            existing = supabase.table("profiles")\
                .select("email")\
                .eq("email", email)\
                .execute()
            
            return {
                "valid": True,
                "exists": len(existing.data) > 0 if existing.data else False,
                "message": "Valid Chargebee email"
            }
        except:
            return {
                "valid": True,
                "exists": False,
                "message": "Valid Chargebee email"
            }
    else:
        return {
            "valid": False,
            "exists": False,
            "message": "Only @chargebee.com email addresses are allowed"
        }