import os
from fastapi import Depends, HTTPException
from starlette import status
from typing import Annotated
from passlib.context import CryptContext
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
from database.database import begin
from database.model_db import User


load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
SCHEME = os.getenv("SCHEME")


def get_db():
    db = begin()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

hashed = CryptContext(schemes=[SCHEME])


def authorization(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    password = hashed.verify(password, user.password)
    if not password:
        return False
    return user


SECRET = SECRET_KEY

Algorithm = ALGORITHM


def authentication(role: str, user_id: int, expiring):
    encode = {'sub': role, 'id': user_id}
    expired = datetime.now() + expiring
    encode.update({'exp': expired})
    return jwt.encode(encode, SECRET, algorithm=Algorithm)


bearer = OAuth2PasswordBearer(tokenUrl="user/login")


async def get_user(token: Annotated[str, Depends(bearer)]):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[Algorithm])
        role: str = payload.get("sub")
        user_id: int = payload.get("id")
        if role is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
        return {
            "role": role,
            "user_id": user_id
        }

    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Timeout session expired!")


def otp_authentication(user_id: int):
    encode = {'id': user_id}
    expiring = datetime.now() + timedelta(minutes=15)
    encode.update({'exp': expiring})
    return jwt.encode(encode, SECRET, algorithm=Algorithm)


async def otp_token_verification(token: str):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[Algorithm])
        user_id: int = payload.get("id")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
        return {"user_id": user_id}
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_400_UNAUTHORIZED, detail="Timeout session expired!")
    


otp_dependency = Annotated[str, Depends(otp_token_verification)]
user_dependency = Annotated[str, Depends(get_user)]
