from pydantic import BaseModel,Field
from typing import Literal


class Token(BaseModel):
    access_token: str
    token_type: Literal["access_token","refresh_token"]
    # token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    name: str
    email: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str
