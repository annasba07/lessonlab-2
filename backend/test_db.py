#!/usr/bin/env python3
"""
Simple script to test database connection and basic operations
Run this after setting up your .env file with Supabase credentials
"""

import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

async def test_database():
    """Test basic database operations"""
    
    # Check environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file based on .env.example")
        return False
    
    try:
        # Initialize Supabase client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        supabase: Client = create_client(url, key)
        
        print("✅ Supabase client initialized")
        
        # Test connection by trying to select from lesson_plans table
        response = supabase.table("lesson_plans").select("count").execute()
        print("✅ Database connection successful")
        
        # Test insert operation (with a dummy user_id)
        test_lesson = {
            "user_id": "00000000-0000-0000-0000-000000000000",  # dummy UUID
            "title": "Test Lesson",
            "topic": "Testing Database",
            "grade": "5",
            "duration": 60,
            "plan_json": {"test": "data"},
            "agent_thoughts": {"test": "thoughts"}
        }
        
        insert_response = supabase.table("lesson_plans").insert(test_lesson).execute()
        
        if insert_response.data:
            print("✅ Insert operation successful")
            lesson_id = insert_response.data[0]["id"]
            
            # Test select operation
            select_response = supabase.table("lesson_plans").select("*").eq("id", lesson_id).execute()
            if select_response.data:
                print("✅ Select operation successful")
                
                # Clean up - delete test record
                delete_response = supabase.table("lesson_plans").delete().eq("id", lesson_id).execute()
                print("✅ Delete operation successful")
                
            else:
                print("❌ Select operation failed")
                return False
        else:
            print("❌ Insert operation failed")
            return False
            
        print("\n🎉 All database tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing database connection and operations...\n")
    success = asyncio.run(test_database())
    
    if not success:
        print("\n📋 Next steps:")
        print("1. Make sure you've created the database schema in Supabase")
        print("2. Check your .env file has correct Supabase credentials")
        print("3. Verify your Supabase project is active")
    else:
        print("\n✨ Database is ready for the lesson planning app!")