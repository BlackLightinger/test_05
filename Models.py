from pydantic import BaseModel, EmailStr
import os
from dotenv import load_dotenv

load_dotenv()  

test_email = os.environ["test_email"]
test_code = os.environ["test_code"]


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserVerify(BaseModel):
    email: EmailStr
    code: str


class PasswordResetRequest(BaseModel):
    email: EmailStr
    old_password: str


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    new_password: str
    code: str
