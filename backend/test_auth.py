#!/usr/bin/env python3
"""
Test script to verify authentication utilities work correctly
This tests the JWT validation logic without needing actual tokens
"""

import os
import asyncio
from unittest.mock import patch, MagicMock
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Import our auth functions
from utils.auth import get_current_user

load_dotenv()

def create_test_jwt(user_id: str = "test-user-123", email: str = "test@example.com", expired: bool = False) -> str:
    """Create a test JWT token for testing"""
    
    # Use a test secret if real one isn't available
    secret = os.getenv("SUPABASE_JWT_SECRET", "test-secret-key-for-testing")
    
    # Create payload
    now = datetime.now(timezone.utc)
    exp_time = now - timedelta(hours=1) if expired else now + timedelta(hours=1)
    
    payload = {
        "sub": user_id,
        "email": email,
        "role": "authenticated",
        "aud": "authenticated",
        "exp": exp_time.timestamp(),
        "iat": now.timestamp()
    }
    
    # Create token
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token

async def test_valid_token():
    """Test authentication with a valid token"""
    print("🧪 Testing valid token...")
    
    try:
        # Create test token
        token = create_test_jwt()
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        # Test authentication
        user = await get_current_user(credentials)
        
        print(f"✅ Valid token test passed")
        print(f"   User ID: {user['user_id']}")
        print(f"   Email: {user['email']}")
        print(f"   Role: {user['role']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Valid token test failed: {str(e)}")
        return False

async def test_expired_token():
    """Test authentication with an expired token"""
    print("\n🧪 Testing expired token...")
    
    try:
        # Create expired token
        token = create_test_jwt(expired=True)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        # This should raise an exception
        user = await get_current_user(credentials)
        print("❌ Expired token test failed: Should have raised an exception")
        return False
        
    except Exception as e:
        if "expired" in str(e).lower():
            print("✅ Expired token test passed: Correctly rejected expired token")
            return True
        else:
            print(f"❌ Expired token test failed: Wrong error - {str(e)}")
            return False

async def test_invalid_token():
    """Test authentication with an invalid token"""
    print("\n🧪 Testing invalid token...")
    
    try:
        # Create invalid token
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid.jwt.token")
        
        # This should raise an exception
        user = await get_current_user(credentials)
        print("❌ Invalid token test failed: Should have raised an exception")
        return False
        
    except Exception as e:
        if "invalid" in str(e).lower() or "malformed" in str(e).lower():
            print("✅ Invalid token test passed: Correctly rejected invalid token")
            return True
        else:
            print(f"❌ Invalid token test failed: Wrong error - {str(e)}")
            return False

async def test_missing_env_var():
    """Test behavior when SUPABASE_JWT_SECRET is missing"""
    print("\n🧪 Testing missing environment variable...")
    
    # Temporarily remove the env var
    original_secret = os.getenv("SUPABASE_JWT_SECRET")
    if "SUPABASE_JWT_SECRET" in os.environ:
        del os.environ["SUPABASE_JWT_SECRET"]
    
    try:
        token = create_test_jwt()
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        # This should raise a 500 error
        user = await get_current_user(credentials)
        print("❌ Missing env var test failed: Should have raised an exception")
        return False
        
    except Exception as e:
        if "configuration" in str(e).lower():
            print("✅ Missing env var test passed: Correctly detected missing config")
            return True
        else:
            print(f"❌ Missing env var test failed: Wrong error - {str(e)}")
            return False
    finally:
        # Restore env var
        if original_secret:
            os.environ["SUPABASE_JWT_SECRET"] = original_secret

async def run_all_tests():
    """Run all authentication tests"""
    print("🔐 Testing Authentication Utilities\n")
    
    tests = [
        test_valid_token,
        test_expired_token, 
        test_invalid_token,
        test_missing_env_var
    ]
    
    results = []
    for test_func in tests:
        result = await test_func()
        results.append(result)
    
    print(f"\n📊 Test Results:")
    print(f"   Passed: {sum(results)}/{len(results)}")
    print(f"   Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 All authentication tests passed!")
        print("✨ The auth system is ready for integration!")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
    
    return all(results)

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)