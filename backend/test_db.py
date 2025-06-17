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
        
        # Test basic table access (without foreign key constraints)
        print("✅ Testing table access...")
        
        # Debug: Test different types of queries
        try:
            # Test 1: Select all records
            print("\n🔍 Debug: Testing SELECT * query...")
            all_response = supabase.table("lesson_plans").select("*").execute()
            print(f"   Raw response: {all_response}")
            print(f"   Data: {all_response.data}")
            print(f"   Data type: {type(all_response.data)}")
            print(f"   Length: {len(all_response.data) if all_response.data else 'None'}")
            
            # Test 2: Select count specifically
            print("\n🔍 Debug: Testing SELECT count query...")
            count_response = supabase.table("lesson_plans").select("count").execute()
            print(f"   Raw response: {count_response}")
            print(f"   Data: {count_response.data}")
            print(f"   Data type: {type(count_response.data)}")
            print(f"   Length: {len(count_response.data) if count_response.data else 'None'}")
            
            # Test 3: Try a proper count query
            print("\n🔍 Debug: Testing COUNT(*) query...")
            try:
                # This might not work with the table() method, but let's try
                real_count = supabase.rpc('count_lesson_plans').execute()
                print(f"   RPC count response: {real_count}")
            except Exception as rpc_error:
                print(f"   RPC count failed (expected): {rpc_error}")
            
            print("✅ Table access successful")
            actual_count = len(all_response.data) if all_response.data else 0
            print(f"✅ Actual lesson plans count: {actual_count}")
            
        except Exception as e:
            print(f"❌ Table access failed: {str(e)}")
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