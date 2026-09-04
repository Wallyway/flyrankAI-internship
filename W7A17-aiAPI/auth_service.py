from fastapi import HTTPException
from supabase import AuthError, Client, create_client
from typing import Optional


class AuthService:
    def __init__(self, url: str, key: str):
        if not url or not key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_KEY are required")
        self.client: Client = create_client(url, key)

    def sign_up(self, email: Optional[str], password: Optional[str]) -> dict:
        self._require_credentials(email, password)
        try:
            response = self.client.auth.sign_up({"email": email, "password": password})
        except AuthError as error:
            raise HTTPException(status_code=400, detail=error.message)
        return {"user": response.user}

    def sign_in(self, email: Optional[str], password: Optional[str]) -> dict:
        self._require_credentials(email, password)
        try:
            response = self.client.auth.sign_in_with_password({"email": email, "password": password})
        except AuthError:
            raise HTTPException(status_code=401, detail="Invalid login credentials")
        if response.session is None:
            raise HTTPException(status_code=401, detail="Email not confirmed")
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": response.session.token_type,
            "expires_in": response.session.expires_in,
            "user": response.user,
        }

    def get_user(self, token: str):
        try:
            response = self.client.auth.get_user(token)
        except AuthError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        if response is None or response.user is None:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return response.user

    def sign_out(self, token: str):
        try:
            self.client.auth.admin.sign_out(token)
        except AuthError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

    @staticmethod
    def _require_credentials(email: Optional[str], password: Optional[str]):
        if not email or not password:
            raise HTTPException(status_code=400, detail="email and password are required")
