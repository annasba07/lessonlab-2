from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timezone

# Set up logging
logger = logging.getLogger(__name__)

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Verify JWT token from Supabase Auth and return user info
    
    Args:
        credentials: JWT token from Authorization header
        
    Returns:
        Dict containing user_id, email, and other user info
        
    Raises:
        HTTPException: If token is invalid or missing required fields
    """
    try:
        token = credentials.credentials
        
        # Validate environment variables
        jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        if not jwt_secret:
            logger.error("SUPABASE_JWT_SECRET environment variable not set")
            raise HTTPException(
                status_code=500, 
                detail="Authentication service configuration error"
            )
        
        # Decode and verify the JWT token
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            audience="authenticated"
        )
        
        # Extract user information from token payload
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role", "authenticated")
        
        # Validate required fields
        if not user_id:
            logger.warning("JWT token missing user ID (sub claim)")
            raise HTTPException(
                status_code=401, 
                detail="Invalid token: missing user identification"
            )
        
        # Check if user is authenticated
        if role != "authenticated":
            logger.warning(f"User {user_id} has invalid role: {role}")
            raise HTTPException(
                status_code=401,
                detail="Invalid token: user not authenticated"
            )
        
        # Check token expiration
        exp = payload.get("exp")
        if exp and exp < datetime.now(timezone.utc).timestamp():
            logger.warning(f"Expired token for user {user_id}")
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
        
        logger.info(f"Successfully authenticated user: {user_id}")
        
        return {
            "user_id": user_id,
            "email": email,
            "role": role,
            "raw_payload": payload
        }
        
    except JWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        error_msg = str(e).lower()
        if "expired" in error_msg:
            raise HTTPException(
                status_code=401, 
                detail="Token has expired"
            )
        else:
            raise HTTPException(
                status_code=401, 
                detail="Invalid or malformed token"
            )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Authentication service error"
        )

async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[Dict[str, Any]]:
    """
    Optional authentication - returns user info if token is provided and valid, None otherwise
    Useful for endpoints that work with or without authentication
    """
    if not credentials:
        return None
    
    try:
        # Convert to required dependency and get user
        return await get_current_user(credentials)
    except HTTPException:
        # If token is invalid, return None instead of raising error
        return None