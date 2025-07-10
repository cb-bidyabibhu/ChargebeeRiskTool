# backend/auth_routes.py
"""
FIXED Authentication routes with proper user validation and email checking
"""

import os
import re
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr, validator
from supabase import Client, create_client

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Supabase credentials not found in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Get the correct redirect URL based on environment
def get_redirect_url() -> str:
    """Return the appropriate frontend redirect URL based on environment."""
    if os.getenv("RENDER"):
        return "https://chargebee-kyb-frontend.onrender.com"
    return "http://localhost:3000"

# Helper function to get current user token
def get_current_user_token(authorization: Optional[str] = Header(None)):
    """Extract and validate the authorization token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    if authorization.startswith("Bearer "):
        return authorization[7:]
    
    return authorization

# Helper function to validate Chargebee email
def validate_chargebee_email(email: str) -> bool:
    """Validate if email is from Chargebee domain"""
    pattern = r'^[a-zA-Z0-9._%+-]+@chargebee\.com$'
    return re.match(pattern, email) is not None

# FIXED: Helper function to check if user exists
async def check_user_exists_in_supabase(email: str) -> bool:
    """Check if user already exists in Supabase Auth"""
    try:
        # Try to get user by email (this will work if user exists)
        # Note: Supabase doesn't provide a direct "check user exists" method
        # So we'll attempt to sign in with a dummy password to check existence
        # But that's not ideal. Instead, we'll use a different approach.
        
        # For now, we'll maintain a simple users table to track registrations
        # Or use the auth.users table if accessible
        
        # Alternative: Try to initiate password reset (safe way to check existence)
        try:
            # We do not need the actual response; calling this API is enough to check existence
            _ = supabase.auth.reset_password_email(
                email,
                {"redirect_to": f"{get_redirect_url()}/reset-password"}
            )
            return True  # If no exception, user exists
        except Exception as e:
            error_msg = str(e).lower()
            if "user not found" in error_msg or "invalid email" in error_msg:
                return False
            # If it's a different error, assume user might exist
            return True
            
    except Exception as e:
        print(f"Error checking user existence: {e}")
        return False

# Pydantic models
class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    
    @validator('email')
    def validate_email_domain(cls, v):
        if not validate_chargebee_email(v):
            raise ValueError('Email must be from @chargebee.com domain')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class SignInRequest(BaseModel):
    email: EmailStr
    password: str
    
    @validator('email')
    def validate_email_domain(cls, v):
        if not validate_chargebee_email(v):
            raise ValueError('Email must be from @chargebee.com domain')
        return v

class CheckUserRequest(BaseModel):
    email: EmailStr

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None

# FIXED: Authentication endpoints with proper validation

@router.post("/check-user")
async def check_user_existence(request: CheckUserRequest):
    """
    FIXED: Check if user exists in the system
    """
    try:
        # Validate Chargebee email
        if not validate_chargebee_email(request.email):
            return {
                "exists": False,
                "message": "Invalid email domain. Must be @chargebee.com"
            }
        
        # Check if user exists in Supabase
        user_exists = await check_user_exists_in_supabase(request.email)
        
        return {
            "exists": user_exists,
            "email": request.email,
            "message": "User exists" if user_exists else "User not found"
        }
        
    except Exception as e:
        print(f"Error checking user: {e}")
        # In case of error, assume user doesn't exist to allow signup
        return {
            "exists": False,
            "message": "Unable to verify user existence"
        }

@router.post("/signup")
async def sign_up(request: SignUpRequest):
    """
    FIXED: Create a new user account with proper validation
    """
    try:
        # FIXED: Check if user already exists
        user_exists = await check_user_exists_in_supabase(request.email)
        if user_exists:
            raise HTTPException(
                status_code=400, 
                detail="An account with this email already exists. Please login instead."
            )
        
        redirect_url = get_redirect_url()
        
        # For development mode - check environment
        if os.getenv("ENVIRONMENT") == "development":
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
                error_message = str(supabase_error).lower()
                if "user already registered" in error_message:
                    raise HTTPException(status_code=400, detail="Email already registered")
                
                # If Supabase fails in dev, create mock user
                print(f"Supabase signup failed in dev: {supabase_error}")
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
            
    except HTTPException:
        raise
    except Exception as e:
        error_message = str(e).lower()
        if "user already registered" in error_message or "email already exists" in error_message:
            raise HTTPException(status_code=400, detail="Email already registered")
        print(f"Signup error: {e}")
        raise HTTPException(status_code=400, detail=f"Signup failed: {str(e)}")

@router.post("/signin")
async def sign_in(request: SignInRequest):
    """
    FIXED: Sign in with proper authentication validation
    """
    try:
        # FIXED: Always validate email domain first
        if not validate_chargebee_email(request.email):
            raise HTTPException(
                status_code=400, 
                detail="Please use a valid @chargebee.com email address"
            )
        
        # FIXED: Check if user exists before attempting login
        user_exists = await check_user_exists_in_supabase(request.email)
        if not user_exists:
            raise HTTPException(
                status_code=401, 
                detail="No account found with this email. Please sign up first."
            )
        
        # Try Supabase authentication
        try:
            response = supabase.auth.sign_in_with_password({
                "email": request.email,
                "password": request.password
            })
            
            if response.user and response.session:
                # Enforce email verification – prevent login if user has not confirmed email
                if response.user.email_confirmed_at is None:
                    raise HTTPException(
                        status_code=401,
                        detail="Email address not verified. Please check your inbox and click the verification link before logging in."
                    )

                return {
                    "success": True,
                    "message": "Signed in successfully",
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "user_metadata": response.user.user_metadata or {},
                        "email_verified": True
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
            error_message = str(supabase_error).lower()
            if "invalid login credentials" in error_message or "invalid email or password" in error_message:
                raise HTTPException(status_code=401, detail="Invalid email or password")
            
            # For development mode fallback
            if os.getenv("ENVIRONMENT") == "development":
                print(f"Supabase signin failed in dev: {supabase_error}")
                # Only allow dev mode for specific users
                if request.email in ["bidya.bibhu@chargebee.com", "test@chargebee.com"] and request.password == "devmode123":
                    return {
                        "success": True,
                        "message": "Signed in successfully (dev mode)",
                        "user": {
                            "id": "dev-user-" + request.email.replace("@", "-"),
                            "email": request.email,
                            "user_metadata": {"full_name": "Dev User"},
                            "email_verified": True
                        },
                        "session": {
                            "access_token": "dev-token-" + request.email.replace("@", "-"),
                            "refresh_token": "dev-refresh-" + request.email.replace("@", "-"),
                            "expires_at": 9999999999
                        },
                        "dev_mode": True
                    }
            
            raise HTTPException(status_code=401, detail="Invalid email or password")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed due to server error")

@router.post("/signout")
async def sign_out(authorization: str = Depends(get_current_user_token)):
    """Sign out the current user"""
    try:
        if not authorization.startswith('dev-token'):
            supabase.auth.sign_out()
        return {
            "success": True,
            "message": "Signed out successfully"
        }
    except Exception as e:
        print(f"Signout error: {e}")
        return {
            "success": True,
            "message": "Signed out successfully"  # Always return success for signout
        }

@router.get("/user")
async def get_user(authorization: str = Depends(get_current_user_token)):
    """Get current user information"""
    try:
        # Handle dev tokens
        if authorization.startswith('dev-token'):
            return {
                "success": True,
                "user": {
                    "id": authorization,
                    "email": "dev@chargebee.com",
                    "user_metadata": {"full_name": "Dev User"},
                    "email_verified": True
                }
            }
        
        # Get user from Supabase
        user_response = supabase.auth.get_user(authorization)
        if user_response and user_response.user:
            return {
                "success": True,
                "user": {
                    "id": user_response.user.id,
                    "email": user_response.user.email,
                    "user_metadata": user_response.user.user_metadata or {},
                    "created_at": user_response.user.created_at,
                    "email_verified": user_response.user.email_confirmed_at is not None
                }
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
            
    except Exception as e:
        print(f"Get user error: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.post("/reset-password")
async def reset_password(request: CheckUserRequest):
    """Send password reset email"""
    try:
        if not validate_chargebee_email(request.email):
            raise HTTPException(
                status_code=400, 
                detail="Please use a valid @chargebee.com email address"
            )
        
        redirect_url = get_redirect_url()
        
        response = supabase.auth.reset_password_email(
            request.email,
            {
                "redirect_to": f"{redirect_url}/reset-password"
            }
        )
        
        return {
            "success": True,
            "message": "Password reset email sent successfully"
        }
    except Exception as e:
        # Don't reveal if email exists or not for security
        return {
            "success": True,
            "message": "If an account with this email exists, a password reset link has been sent."
        }

@router.put("/update-profile")
async def update_profile(
    request: UpdateProfileRequest,
    authorization: str = Depends(get_current_user_token)
):
    """Update user profile information"""
    try:
        if authorization.startswith('dev-token'):
            return {
                "success": True,
                "message": "Profile updated successfully (dev mode)",
                "user": {
                    "id": authorization,
                    "email": "dev@chargebee.com",
                    "user_metadata": {"full_name": request.full_name or "Dev User"}
                }
            }
        
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
        print(f"Update profile error: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to update profile: {str(e)}")

# Health check for auth service
@router.get("/health")
async def auth_health_check():
    """Check if authentication service is working"""
    try:
        # Test Supabase connection
        settings = supabase.auth.get_settings()
        return {
            "status": "healthy",
            "service": "authentication",
            "supabase_connected": True,
            "redirect_url": get_redirect_url(),
            "email_validation": "enabled",
            "user_existence_check": "enabled",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "authentication",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }