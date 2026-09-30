from datetime import datetime, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pwdlib import PasswordHash

from config.settings import settings
from database.operations.auth import create_user, login_user
from database.operations.auth_sessions import (
    create_auth_session,
    get_auth_session,
    update_session_last_used,
    revoke_auth_session,
)
from utils.jwt import create_access_token, create_refresh_token
from utils.token_hash import hash_token


security = HTTPBearer()

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM


def create_registered_user(name: str, email: str, password: str):
    try:
        password_hash = PasswordHash.recommended()

        hashed_password = password_hash.hash(password)

        create_user(
            name=name,
            email=email,
            password=hashed_password,
        )

        return {
            "message": "user created successfully",
            "success": True,
        }

    except ValueError as e:
        return {
            "message": f"user creation failed {e}",
            "success": False,
        }

    except Exception as e:
        print(f"User creation error: {e}")

        return {
            "message": "user creation failed",
            "success": False,
        }


def authenticate_user(
    email: str,
    password: str,
    device_name: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
):
    try:
        user = login_user(email)

        if not user:
            return {
                "message": "no user has registered with this email",
                "success": False,
            }

        user_id = user[0]
        stored_password = user[1]

        password_hash = PasswordHash.recommended()

        if not password_hash.verify(password, stored_password):
            return {
                "message": "invalid email or incorrect password",
                "success": False,
            }

        # Short-lived token
        access_token = create_access_token(user_id)

        # Long-lived token
        refresh_token, refresh_expires_at = create_refresh_token(user_id)

        # Never store the actual refresh token in DB
        refresh_token_hash = hash_token(refresh_token)

        create_auth_session(
            user_id=user_id,
            token_hash=refresh_token_hash,
            device_name=device_name,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=refresh_expires_at,
        )

        return {
            "message": "login successful",
            "success": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    except Exception as e:
        print(f"Login error: {e}")

        return {
            "message": "user login failed",
            "success": False,
        }


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")
        token_type = payload.get("type")

        if user_id is None or token_type != "access":
            raise HTTPException(
                status_code=401,
                detail="Invalid access token",
            )

        return int(user_id)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired",
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )


def refresh_access_token(refresh_token: str):
    # Hash the incoming refresh token
    token_hash = hash_token(refresh_token)

    # Find the session associated with this token
    session = get_auth_session(token_hash)

    if not session:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    session_id = session[0]
    user_id = session[1]
    expires_at = session[2]
    revoked_at = session[3]

    # Check whether session was revoked
    if revoked_at is not None:
        raise HTTPException(
            status_code=401,
            detail="Session has been revoked",
        )

    # Check database session expiry
    if expires_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=401,
            detail="Refresh token expired",
        )

    try:
        # Verify JWT signature and JWT expiry
        payload = jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        # Make sure this is actually a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token",
            )

        token_user_id = payload.get("sub")

        if token_user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token",
            )

        # Make sure JWT user matches DB session user
        if int(token_user_id) != user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token",
            )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Refresh token expired",
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    # Token was successfully used
    update_session_last_used(session_id)

    # Issue a new access token
    new_access_token = create_access_token(user_id)

    return {
        "access_token": new_access_token,
    }


def logout(refresh_token: str):
    token_hash = hash_token(refresh_token)
    session = get_auth_session(token_hash)
    # Logout is idempotent
    if not session:
        return {
            "message": "Logged out",
            "success": True,
        }
    revoke_auth_session(session[0])

    return {
        "message": "Logged out",
        "success": True,
    }

# def logout_all_sessions(user_id: int):
#     revoke_all_user_sessions(user_id)

#     return {
#         "message": "All sessions logged out",
#         "success": True,
#     }