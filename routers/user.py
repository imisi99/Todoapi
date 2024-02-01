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

#User Authorization and Authentication 
hash = CryptContext(schemes= ["bcrypt"])
db_dependency = Annotated[str, Depends(get_db)]


def authorization(username : str , password: str , db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    password = hash.hash(password, user.password)
    if not password:
        return False
    return user

SECRECT = '488134d4d7e4205c8960dcb67c689fceba88ef1476126a7f9d78093bbb64150fd7f2652b081826475b73a76b73829e821f72cfd313a363f6e1db3927caaf46ba88c0c12d66e9cb0e2104262f29bdba91359d181497790424c298c26c2f4776187b5cb8d9f6afd3bc975cb207af2b057c6561cea6ff686b2bdc8fb5ad0244838c'
Algorithm = 'HS256'

def access(username : str, user_id : int, timedelta):
    encode = {'sub' : username , 'id' : user_id}
    expired = datetime.utcnow() + timedelta
    encode.update({'exp' : expired})
    return jwt.encode(encode, SECRECT, algorithm= Algorithm)

bearer = OAuth2PasswordBearer(tokenUrl="user/login")

def get_user(token : Annotated[str, Depends(bearer)]):
    try:
        payload = jwt.decode(token, SECRECT, algorithms= Algorithm)
        username : str = payload.get("sub")
        user_id : int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Invalid username or password!")
        
        return {
            "username" : username,
            "user_id" : user_id
        }
    except JWTError:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Invalid username or password!")
        
user_dependancy = Annotated[str, Depends(get_user)]
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

        


#User Singup route
#User login route
#User get details route
#User update details route 
#User change password route 
#User forgot password route 
#User delete route