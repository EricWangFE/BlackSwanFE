"""Authentication API routes"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import bcrypt
from datetime import datetime, timedelta

from shared.middleware.auth import AuthMiddleware
from shared.utils.logger import get_logger
from config.settings import settings

logger = get_logger()
router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# Initialize auth middleware
auth = AuthMiddleware(secret_key=settings.jwt_secret_key)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """User login"""
    try:
        # TODO: Verify against database
        # For demo, accept any login
        if len(request.password) < 6:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
        
        # Create token
        token = auth.create_access_token(
            user_id=request.email,
            role="user"
        )
        
        return TokenResponse(access_token=token)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login failed", error=str(e))
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """User registration"""
    try:
        # Validate password
        if len(request.password) < 8:
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 8 characters"
            )
        
        # Hash password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), salt)
        
        # TODO: Save to database
        # For now, just create token
        token = auth.create_access_token(
            user_id=request.email,
            role="user"
        )
        
        return TokenResponse(access_token=token)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Registration failed", error=str(e))
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/refresh")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Refresh access token"""
    try:
        # Verify current token
        payload = await auth.verify_token(credentials)
        
        # Create new token
        new_token = auth.create_access_token(
            user_id=payload["sub"],
            role=payload.get("role", "user")
        )
        
        return TokenResponse(access_token=new_token)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(status_code=500, detail="Token refresh failed")


@router.get("/me")
async def get_current_user(
    user_data: dict = Depends(auth.verify_token)
):
    """Get current user info"""
    return {
        "user_id": user_data["sub"],
        "role": user_data.get("role", "user"),
        "email": user_data["sub"]  # Using email as ID for now
    }