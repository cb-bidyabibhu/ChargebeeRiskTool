# backend/auth_routes.py
"""
Authentication routes with proper redirect URL configuration
FIXED: Moved get_current_user_token before its usage
"""

import os
from fastapi import APIRouter, HTTPException, Depends, Request, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, validator
from supabase import create_client, Client
from typing import Optional, Dict, Any
from datetime import datetime
import re

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Supabase credentials not found in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Get the correct redirect URL based on environment
def get_redirect_url():
    """Get the appropriate redirect URL based on environment"""
    # Check if we're in production (Render)
    if os.getenv("RENDER"):
        return "https://chargebee-kyb-frontend.onrender.com"
    # Default to localhost for development
    return "http://localhost:3000"

# Helper function to get current user token - MOVED BEFORE ITS USAGE
def get_current_user_token(authorization: Optional[str] = Header(None)):
    """
    Extract and validate the authorization token
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # Remove "Bearer " prefix if present
    if authorization.startswith("Bearer "):
        return authorization[7:]
    
    return authorization

# Pydantic models
class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None

# Authentication endpoints
@router.post("/signup")
async def sign_up(request: SignUpRequest):
    """
    Create a new user account with email verification
    """
    try:
        # Get the correct redirect URL
        redirect_url = get_redirect_url()
        
        # For development - skip Supabase if not configured properly
        if os.getenv("ENVIRONMENT") == "development":
            # Check if Supabase is properly configured
            try:
                # Create user with Supabase Auth
                response = supabase.auth.sign_up({
                    "email": request.email,
                    "password": request.password,
                    "options": {
                        "email_redirect_to": redirect_url,
                        "data": {
                            "full_name": request.full_name,
                            "company_name": request.company_name,
                            "created_at": datetime.now().isoformat()
                        }
                    }
                })
                
                if response.user:
                    return {
                        "success": True,
                        "message": "User created successfully. Please check your email to verify your account.",
                        "user_id": response.user.id,
                        "email": response.user.email,
                        "redirect_url": redirect_url
                    }
            except Exception as supabase_error:
                # If Supabase fails in dev, create mock user
                print(f"Supabase signup failed: {supabase_error}")
                return {
                    "success": True,
                    "message": "User created successfully (dev mode - no email verification needed)",
                    "user_id": "dev-" + request.email.replace("@", "-"),
                    "email": request.email,
                    "redirect_url": redirect_url,
                    "dev_mode": True
                }
        
        # Production mode - use Supabase normally
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "email_redirect_to": redirect_url,
                "data": {
                    "full_name": request.full_name,
                    "company_name": request.company_name,
                    "created_at": datetime.now().isoformat()
                }
            }
        })
        
        if response.user:
            return {
                "success": True,
                "message": "User created successfully. Please check your email to verify your account.",
                "user_id": response.user.id,
                "email": response.user.email,
                "redirect_url": redirect_url
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to create user")
            
    except Exception as e:
        error_message = str(e)
        if "User already registered" in error_message:
            raise HTTPException(status_code=400, detail="Email already registered")
        raise HTTPException(status_code=400, detail=error_message)

@router.post("/signin")
async def sign_in(request: SignInRequest):
    """
    Sign in with email and password
    """
    try:
        # For development/testing - allow simple auth bypass
        if os.getenv("ENVIRONMENT") == "development" and request.email.endswith("@chargebee.com"):
            # First check if it's a known dev user
            known_dev_users = {
                "bidya.bibhu@chargebee.com": "Bidya Sharma",
                "test@chargebee.com": "Test User"
            }
            
            if request.email in known_dev_users or request.password == "devmode123":
                # Mock response for development
                return {
                    "success": True,
                    "message": "Signed in successfully (dev mode)",
                    "user": {
                        "id": "dev-user-" + request.email.replace("@", "-"),
                        "email": request.email,
                        "user_metadata": {"full_name": known_dev_users.get(request.email, "Dev User")}
                    },
                    "session": {
                        "access_token": "dev-token-" + request.email.replace("@", "-"),
                        "refresh_token": "dev-refresh-" + request.email.replace("@", "-"),
                        "expires_at": 9999999999
                    }
                }
        
        # Try Supabase auth
        try:
            response = supabase.auth.sign_in_with_password({
                "email": request.email,
                "password": request.password
            })
            
            if response.user:
                return {
                    "success": True,
                    "message": "Signed in successfully",
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "user_metadata": response.user.user_metadata
                    },
                    "session": {
                        "access_token": response.session.access_token,
                        "refresh_token": response.session.refresh_token,
                        "expires_at": response.session.expires_at
                    }
                }
            else:
                raise HTTPException(status_code=401, detail="Invalid credentials")
        except Exception as supabase_error:
            # In development, be more lenient
            if os.getenv("ENVIRONMENT") == "development":
                print(f"Supabase signin failed: {supabase_error}")
                # Still return error but with helpful message
                raise HTTPException(
                    status_code=401, 
                    detail="Login failed. In dev mode, use password 'devmode123' for any @chargebee.com email"
                )
            else:
                raise HTTPException(status_code=401, detail="Invalid email or password")
            
    except HTTPException:
        raise
    except Exception as e:
        error_message = str(e)
        if "Invalid login credentials" in error_message:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        raise HTTPException(status_code=400, detail=error_message)

@router.post("/signout")
async def sign_out(authorization: str = Depends(get_current_user_token)):
    """
    Sign out the current user
    """
    try:
        supabase.auth.sign_out()
        return {
            "success": True,
            "message": "Signed out successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user")
async def get_user(authorization: str = Depends(get_current_user_token)):
    """
    Get current user information
    """
    try:
        user = supabase.auth.get_user(authorization)
        if user:
            return {
                "success": True,
                "user": {
                    "id": user.user.id,
                    "email": user.user.email,
                    "user_metadata": user.user.user_metadata,
                    "created_at": user.user.created_at
                }
            }
        else:
            raise HTTPException(status_code=401, detail="Not authenticated")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.post("/reset-password")
async def reset_password(email: EmailStr):
    """
    Send password reset email
    """
    try:
        redirect_url = get_redirect_url()
        
        response = supabase.auth.reset_password_email(
            email,
            {
                "redirect_to": f"{redirect_url}/reset-password"
            }
        )
        
        return {
            "success": True,
            "message": "Password reset email sent successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/update-profile")
async def update_profile(
    request: UpdateProfileRequest,
    authorization: str = Depends(get_current_user_token)
):
    """
    Update user profile information
    """
    try:
        update_data = {}
        if request.full_name is not None:
            update_data["full_name"] = request.full_name
        if request.company_name is not None:
            update_data["company_name"] = request.company_name
        if request.phone is not None:
            update_data["phone"] = request.phone
            
        response = supabase.auth.update_user({
            "data": update_data
        })
        
        if response.user:
            return {
                "success": True,
                "message": "Profile updated successfully",
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "user_metadata": response.user.user_metadata
                }
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to update profile")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Health check for auth service
@router.get("/health")
async def auth_health_check():
    """
    Check if authentication service is working
    """
    try:
        # Test Supabase connection
        settings = supabase.auth.get_settings()
        return {
            "status": "healthy",
            "service": "authentication",
            "supabase_connected": True,
            "redirect_url": get_redirect_url(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "authentication",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }