from fastapi import APIRouter,Depends
from api.controllers.auth import create_registered_user,authenticate_user,get_current_user
from pydantic import BaseModel, EmailStr

router = APIRouter()


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
class LoginRequest(BaseModel):
    email:EmailStr
    password:str

@router.post("/add/user")
def register_user(data: RegisterRequest):
    return create_registered_user(
        name=data.name, email=data.email, password=data.password
    )
@router.post('/login/user')
def login_user(data:LoginRequest):
    return authenticate_user(
        email=data.email,password=data.password
    )
@router.get('/my/profile')
def profile(user_id : int = Depends(get_current_user)):
    return {
        "user_id":user_id
    }

