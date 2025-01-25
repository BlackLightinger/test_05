from pydantic import BaseModel, EmailStr
import os
from dotenv import load_dotenv

load_dotenv()  

test_email = os.environ["TEST_EMAIL"]
test_code = os.environ["TEST_CODE"]


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
