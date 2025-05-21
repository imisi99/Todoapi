import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Annotated



class SignupForm(BaseModel):
    firstname: Annotated[str, Field()]
    lastname: Annotated[str, Field()]
    username: Annotated[str, Field()]
    email: Annotated[EmailStr, Field]
    password: Annotated[str, Field()]

    @field_validator("password")
    def check_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long!.")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one uppercase letter!.")
        if not re.search(r'[!@#$%^&*(),.?:{}|<>]', value):
            raise ValueError("Password must contain at least one special character!.")
        return value

    @field_validator("username")
    def check_username(cls, value):
        if len(value) < 8:
            raise ValueError("Username must be at least 8 characters long")
        if len(value) > 12:
            raise ValueError("Username is too long")
        return value.replace(" ", "")



class LoginForm(BaseModel):
    username: Annotated[str, Field]
    password: Annotated[str, Field]



class UpdateUser(BaseModel):
    firstname: Annotated[str, Field()]
    lastname: Annotated[str, Field()]
    username: Annotated[str, Field()]
    email: Annotated[EmailStr, Field]
    
    @field_validator("username")
    def check_username(cls, value):
        if len(value) < 8:
            raise ValueError("Username must be at least 8 characters long")
        if len(value) > 12:
            raise ValueError("Username is too long")
        return value.replace(" ", "")    



class NewPassword(BaseModel):
    password: Annotated[str, Field()]
    new_password: Annotated[str, Field()]
    confirm_password: Annotated[str, Field()]

    @field_validator("new_password")
    def check_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long!.")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one upper-case character!.")
        if not re.search(r'[!@#$%^&*(),.?:{}|<>]', value):
            raise ValueError("Password must contain at least one special character!.")
        return value



class ForgotPassowrd(BaseModel):
    new_password: Annotated[str, Field()]
    confirm_password: Annotated[str, Field()]

    @field_validator("new_password")
    def check_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long!.")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one upper-case character!.")
        if not re.search(r'[!@#$%^&*(),.?:{}|<>]', value):
            raise ValueError("Password must contain at least one special character!.")
        return value



class OTPGeneration(BaseModel):
    email: Annotated[EmailStr, Field]
    


class OTPVerification(BaseModel):
    otp: Annotated[str, Field]

    
    
class UserDetails(BaseModel):
    firstname: str
    lastname: str
    username: str
    email: EmailStr
    
    
    
class Token(BaseModel):
    access_token: str
    token_type: str
    