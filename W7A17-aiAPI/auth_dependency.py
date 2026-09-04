from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase_auth import User
from typing import Optional

from auth_service import AuthService

bearer_scheme = HTTPBearer(auto_error=False, description="Paste the access_token returned by POST /auth/login")


def get_auth(request: Request) -> AuthService:
    return request.app.state.auth


def get_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer" or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Access token required")
    return credentials.credentials


def require_user(token: str = Depends(get_token), auth: AuthService = Depends(get_auth)) -> User:
    return auth.get_user(token)
