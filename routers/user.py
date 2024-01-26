from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from pydantic import BaseModel, Field, EmailStr, validator
from starlette import status
from schemas.database import engine, begin
import schemas.model_db as model_db
from schemas.model_db import User
from .todo import get_db
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
import re
from datetime import timedelta, datetime
from passlib.context import CryptContext

user = APIRouter()
#Initializing the DB
model_db.data.metadata.create_all(bind = engine)
db_dependency = Annotated[str, Depends(get_db)]


user_dependancy = Annotated[str, Depends()]


#Creating the pydantic validattion for the user signup form 
class UserForm(BaseModel):
    firstname : Annotated[str, Field(min_length= 3, max_length= 50)]
    lastname : Annotated[str, Field(min_length= 3, max_length= 50)]
    username : Annotated[str, Field(min_length=3 , max_length= 15)]
    email : Annotated[EmailStr, Field]
    password : Annotated[str, Field(min_length= 8 , description= "Password must conatain at least 8 character, one special character, and one Upper case letter")]


    @validator("password")
    def check_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long!.")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one uppercase letter!.")
        if not re.search(r'[!@#$%^&*(),.?:{}|<>]',value):
            raise ValueError("Password must contain at least one special character!.")


    class Config():
        json_schema_extra = {
            'example' : {
                "firstname" : "Firstname",
                "lastname" : "Lastname",
                "username" : "Username",
                "gmail" : "email@gmail.com",
                "password" : "Password"
            }
        }

#Login form class
class LoginForm(BaseModel):
    username : Annotated[str, Field]
    password : Annotated[str, Field]

    class Config():
        json_schema_extra = {
            'example' : {
                "username" : "Username",
                "password" : "Password"
            }
        }

#Update details class 
class UpdateUser(BaseModel):
    firstname : Annotated[str, Field(min_length= 3, max_length= 20)]
    lastname : Annotated[str, Field(min_length=3, max_length= 20)]
    username : Annotated[str, Field(min_length= 3, max_length= 15)]
    email : Annotated[EmailStr, Field]

    class Config():
        json_schema_extra = {
            'example' : {
                "firstname" : "Firstname",
                "lastname" : "Lastname",
                "username" : "Username",
                "email" : "email@gmail.com"
            }
        }

#Change password class
class NewPassword(BaseModel):
    new_password : Annotated[str, Field(min_length= 8, description= "Password must conatain at least 8 character, one special character, and one Upper case letter")]
    confirm_password : Annotated[str, Field()]

    @validator("new_password")
    def check_password(cls, value):
        if len(value) < 8 :
            raise ValueError("Password must be at least 8 characters long!.")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at leat one upper-case character!.")
        if not re.search(r'[!@#$%^&*(),.?:{}|<>]', value):
            raise ValueError("Password must contain at least one special character!.")
        
        
    class Config():
        json_schema_extra = {
            'example' : {
                "new_password" : "new_password",
                "confirm_password" : "confirm_password"
            }
        }
#Forgotten user password 
class ChangePassword(BaseModel):
    username : Annotated[str, Field(min_length= 3, max_length= 15)]
    new_password : Annotated[str, Field(min_length= 8, description= "Password must conatain at least 8 character, one special character, and one Upper case letter")]
    confirm_password : Annotated[str, Field]

    @validator("new_password")
    def check_password(cls, value):
        if len(value) < 8 :
            raise ValueError("Password must be at least 8 characters long!.")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one upper-case character!.")
        if not re.search(r'[!@#$%^&*(),.?:{}|<>]'):
            raise ValueError("Password must contain at least one special character!.")
        
    class Config():
        json_schema_extra = {
            'example' : {
                "username" : "Username",
                "password" : "Password",
                "confirm password" : " re-type Password"
            }
        }

#User Authorization and Authentication 
        
hash = CryptContext(schemes= ["bcrypt"])

#User Singup route
#User login route
#User get details route
#User update details route 
#User change password route 
#User forgot password route 
#User delete route