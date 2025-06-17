from supabase import create_client, Client
import os

class AuthService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.supabase: Client = create_client(url, key)
    
    async def login(self, email: str, password: str):
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return {
                "access_token": response.session.access_token,
                "user": response.user.dict()
            }
        except Exception as e:
            raise Exception(f"Login failed: {str(e)}")
    
    async def register(self, email: str, password: str):
        try:
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            return {
                "message": "Registration successful",
                "user": response.user.dict() if response.user else None
            }
        except Exception as e:
            raise Exception(f"Registration failed: {str(e)}")