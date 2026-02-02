import os
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWKClient
from pydantic import BaseModel
from supabase import create_client, Client
import ssl
import certifi

security = HTTPBearer()

# Cache the JWKS client
_jwks_client: Optional[PyJWKClient] = None


def get_jwks_client() -> PyJWKClient:
    """Get or create cached JWKS client for Supabase."""
    global _jwks_client
    if _jwks_client is None:
        supabase_url = os.getenv("SUPABASE_URL")
        if not supabase_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SUPABASE_URL not configured",
            )
        # Supabase JWKS endpoint
        jwks_url = f"{supabase_url}/auth/v1/.well-known/jwks.json"
        # Create SSL context with certifi certificates for macOS compatibility
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        _jwks_client = PyJWKClient(jwks_url, cache_keys=True, ssl_context=ssl_context)
    return _jwks_client


class User(BaseModel):
    id: str
    email: Optional[str] = None


def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase configuration missing",
        )
    return create_client(url, key)


def get_user_supabase_client(token: str) -> Client:
    """Create a Supabase client with user's JWT for RLS."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    if not url or not key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase configuration missing",
        )
    client = create_client(url, key)
    client.auth.set_session(token, token)
    return client


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """Verify JWT and extract user information."""
    token = credentials.credentials

    try:
        # Get signing key from Supabase JWKS endpoint
        jwks_client = get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        # Decode and verify the token
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "HS256"],  # Support both algorithms
            options={"verify_aud": False},
        )

        user_id = payload.get("sub")
        email = payload.get("email")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
            )

        return User(id=user_id, email=email)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}",
        )
