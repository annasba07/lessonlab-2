from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx
import os
from typing import Dict, Any
from functools import lru_cache

security = HTTPBearer()

@lru_cache(maxsize=1)
def get_jwks():
    """Cache JWKS from Supabase to avoid hitting the endpoint on every request"""
    supabase_url = os.getenv("SUPABASE_URL")
    if not supabase_url:
        raise ValueError("SUPABASE_URL environment variable is required")
    
    # Fetch JWKS from Supabase
    jwks_url = f"{supabase_url}/auth/v1/jwks"
    try:
        response = httpx.get(jwks_url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch JWKS: {str(e)}")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify JWT token from Supabase Auth and return user info"""
    try:
        token = credentials.credentials
        jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        
        if not jwt_secret:
            raise HTTPException(status_code=500, detail="SUPABASE_JWT_SECRET not configured")
        
        # Decode and verify the JWT token
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            audience="authenticated"
        )
        
        # Extract user information
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing user ID")
        
        return {
            "user_id": user_id,
            "email": email,
            "raw_payload": payload
        }
        
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")