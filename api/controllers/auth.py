from database.operations.auth import create_user, login_user
from pwdlib import PasswordHash
from utils.jwt import create_access_token, create_refresh_token
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from dotenv import load_dotenv
import os

load_dotenv()

security = HTTPBearer()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"


def create_registered_user(name: str, email: str, password: str):
    try:
        password_hash = PasswordHash.recommended()

        hashed_password = password_hash.hash(password)
        create_user(name=name, email=email, password=hashed_password)
        return {"message": "user created successfully", "success": True}
    except ValueError as e:
        return {"message": f"user creation failed {e}", "success": False}
    except Exception:
        return {"message": "user creation failed", "success": False}


def authenticate_user(email: str, password: str):
    try:
        user = login_user(email)
        if not user:
            return {
                "message": "no user has registered with this email failed",
                "success": False,
            }
        user_id = user[0]
        stored_password = user[1]
        password_hash = PasswordHash.recommended()

        if not password_hash.verify(password, stored_password):
            return {"message": "invalid email or incorrect password", "success": False}

        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)
        return {
            "message": "login successful",
            "success": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    except Exception:
        return {"message": "user login failed", "success": False}


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")
        token_type = payload.get("type")

        if user_id is None or token_type != "access":
            raise HTTPException(
                status_code=401,
                detail="Invalid access token"
            )

        return int(user_id)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
