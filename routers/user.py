from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from pydantic import BaseModel, Field, EmailStr, validator
from starlette import status
from schemas.database import engine, begin
import schemas.model_db as model_db
from schemas.model_db import Todo, User
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
import re
from datetime import timedelta, datetime
from passlib.context import CryptContext
from sqlalchemy.orm import Session

user = APIRouter()

#Initializing the DB
model_db.data.metadata.create_all(bind = engine)

def get_db():
    db =begin()
    try:
        yield db
    finally:
        db.close()
    
db_dependency = Annotated[Session, Depends(get_db)]

#User Authorization and Authentication 

hash = CryptContext(schemes= ["bcrypt"])

def authorization(username : str , password: str , db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    password = hash.verify(password, user.password)
    if not password:
        return False
    return user

SECRECT = '488134d4d7e4205c8960dcb67c689fceba88ef1476126a7f9d78093bbb64150fd7f2652b081826475b73a76b73829e821f72cfd313a363f6e1db3927caaf46ba88c0c12d66e9cb0e2104262f29bdba91359d181497790424c298c26c2f4776187b5cb8d9f6afd3bc975cb207af2b057c6561cea6ff686b2bdc8fb5ad0244838c'
Algorithm = 'HS256'

def authentication(username : str, user_id : int, timedelta):
    encode = {'sub' : username , 'id' : user_id}
    expired = datetime.utcnow() + timedelta
    encode.update({'exp' : expired})
    return jwt.encode(encode, SECRECT, algorithm= Algorithm)

bearer = OAuth2PasswordBearer(tokenUrl="user/login")
async def get_user(token : Annotated[str, Depends(bearer)]):
    try:
        payload = jwt.decode(token, SECRECT, algorithms= [Algorithm])
        username : str = payload.get("sub")
        user_id : int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Unauthorized user")
        return {
            "username" : username,
            "user_id" : user_id
        }
    
    except JWTError as e:
        print(f"JWTError occurred: {e}")
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Error while decoding token please try again later")
        
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
        return value

    class Config():
        json_schema_extra = {
            'example' : {
                "firstname" : "Firstname",
                "lastname" : "Lastname",
                "username" : "Username",
                "email" : "email@gmail.com",
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
    password : Annotated[str, Field()]
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
        return value
        
    class Config():
        json_schema_extra = {
            'example' : {
                "password" : "password",
                "new_password" : "new_password",
                "confirm_password" : "confirm_password"
            }
        }

#Forgotten user password 
class ChangePassword(BaseModel):
    email : Annotated[EmailStr, Field()]
    username : Annotated[str, Field(min_length= 3, max_length= 15)]
    new_password : Annotated[str, Field(min_length= 8, description= "Password must conatain at least 8 character, one special character, and one Upper case letter")]
    confirm_password : Annotated[str, Field]

    @validator("new_password")
    def check_password(cls, value):
        if len(value) < 8 :
            raise ValueError("Password must be at least 8 characters long!.")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one upper-case character!.")
        if not re.search(r'[!@#$%^&*(),.?:{}|<>]', value):
            raise ValueError("Password must contain at least one special character!.")
        return value
    
    class Config():
        json_schema_extra = {
            'example' : {
                "email" : "email@email.com",
                "username" : "Username",
                "new_password" : "Password",
                "confirm_password" : "confirm password"
            }
        }

#Login Token class
class Token(BaseModel):
    access_token : str
    token_type : str


#Logged in user class
class UserDetails(BaseModel):
    firstname : str
    lastname : str
    email : EmailStr
    username : str


#User Singup route
@user.post("/signup", status_code= status.HTTP_201_CREATED)
async def user_signup(userform : UserForm, db : db_dependency):
    signup = False
    existing_username = db.query(User).filter(User.username == userform.username).first()
    existing_email = db.query(User).filter(User.email == userform.email).first()
    if existing_username:
        raise HTTPException(status_code= status.HTTP_226_IM_USED, detail= "username is already in use!")
    
    if existing_email:
        raise HTTPException(status_code= status.HTTP_226_IM_USED, detail= "email is already in use!")
    
    user = User(
        firstname = userform.firstname,
        lastname = userform.lastname,
        username = userform.username,
        email = userform.email,
        password = hash.hash(userform.password)

    )
    signup = True

    if signup is not True:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "Error in trying to validate user")
    
    db.add(user)
    db.commit()
    db.refresh(user)

    return "User has been created successfully"


#User login route
@user.post("/login", response_model= Token, status_code= status.HTTP_202_ACCEPTED)
async def user_login(login : Annotated[OAuth2PasswordRequestForm, Depends()], db : db_dependency):
    user = authorization(login.username, login.password, db)
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Invalid username or password")
    
    token = authentication(user.username, user.id, timedelta(minutes= 200))

    if not token:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "Error trying to log you in please try again later")
    
    return {
        "access_token" : token,
        "token_type" : "bearer"
    }
    

#Get logged in user details route
@user.get("/get-user-details", status_code= status.HTTP_200_OK)
async def get_current_user_details(user : user_dependancy, db : db_dependency):
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Unauthorized user")
    
    user_data = db.query(User).filter(User.id == user.get("user_id")).first()

    if user_data is not None:
        data = UserDetails(
            firstname = user_data.firstname,
            lastname = user_data.lastname,
            email = user_data.email,
            username = user_data.username,
        )

        return data
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= "Error in getting user details, please try again later")


#User update details route 
@user.put("/update-user-details", status_code= status.HTTP_202_ACCEPTED)
async def update_user_details(user : user_dependancy, form : UpdateUser, db : db_dependency):
    user_update = False
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Unauthorized user")
    
    existing_email = db.query(User).filter(User.email == form.email).first()
    existing_username = db.query(User).filter(User.username == form.username).first()

    if existing_email is not None:
        raise HTTPException(status_code= status.HTTP_226_IM_USED, detail= "email is already in use")
    
    if existing_username is not None:
        raise HTTPException(status_code= status.HTTP_226_IM_USED, detail= "username is already in use")
    
    user1 = db.query(User).filter(User.id == user.get("user_id")).first()

    if user1 is None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Invalid login credentials")
    
    user1.firstname = form.firstname
    user1.lastname = form.lastname
    user1.email = form.email
    user1.username = form.username

    user_update = True

    if user_update is not True:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "An error occured while trying to update user, please try again later")
    

    db.add(user1)
    db.commit()
    db.refresh(user1)

    return "User details have been Updated successfully"


#User change password route 
@user.put("/change-user-password", status_code= status.HTTP_202_ACCEPTED)
async def change_user_password(user : user_dependancy, form : NewPassword , db : db_dependency):
    password_changed = False
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Unauthorized user")
    
    user1 = db.query(User).filter(User.id == user.get("user_id")).first()

    if not user1:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Invalid login credentials")
    
    password = hash.verify(form.password, user1.password)
    if not password:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Invalid Password! ")
    
    if form.new_password != form.confirm_password:
        raise HTTPException(status_code= status.HTTP_422_UNPROCESSABLE_ENTITY, detail= "Password does not match")
    
    user1.password = hash.hash(form.new_password)
    
    password_changed = True

    if password_changed is not True:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "Error while trying to process new password, please try again later")
    

    db.add(user1)
    db.commit()
    db.refresh(user1)

    return "Password has been Updated Successfully"


#User forgot password route 
@user.put("/forgot-password", status_code= status.HTTP_202_ACCEPTED)
async def user_forgot_password(db : db_dependency, form : ChangePassword):
    password_changed = False
    user = db.query(User).filter(User.username == form.username).filter(User.email == form.email).first()

    if not user:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Invalid user credentials!")
    
    if form.new_password != form.confirm_password:
        raise HTTPException(status_code= status.HTTP_422_UNPROCESSABLE_ENTITY, detail= "Password does not match")
    
    user.password = hash.hash(form.new_password)
    
    password_changed = True

    if password_changed is not True:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "Error while trying to process new password, please try again later")
    
    db.add(user)
    db.commit()
    db.refresh(user)

    return "Password has been changed successfully"


#User delete route
@user.delete("/delete-user")
async def delete_user(user : user_dependancy, db : db_dependency):
    user_deleted = False
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Unauthorized user")
    
    delete = db.query(User).filter(User.id == user.get("user_id")).first()
    todo = db.query(Todo).filter(Todo.user_id == user.get("user_id")).delete()

    if not delete:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "Error while deleting user data")
    
    if not todo:
       pass
    
    user_deleted = True

    if user_deleted is not True:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "Error while deleting user, please try again later")
    
    db.delete(delete)
    db.commit()

    return "User has been deleted successfully"