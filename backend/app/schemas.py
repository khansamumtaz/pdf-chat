from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class SignupIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

class VerifyOTPIn(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=6, max_length=6)

class EmailIn(BaseModel):
    email: EmailStr

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MessageOut(BaseModel):
    message: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    model_config = {"from_attributes": True}

class ProfileUpdateIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)

class ChangePasswordIn(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=72)

class ResetPasswordIn(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=8, max_length=72)

class DocumentOut(BaseModel):
    id: int
    filename: str
    num_chunks: int
    created_at: datetime
    model_config = {"from_attributes": True}

class UploadOut(BaseModel):
    uploaded: list[DocumentOut]
    errors: list[str]