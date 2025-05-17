import os
from fastapi import Depends, HTTPException
from starlette import status
from typing import Annotated
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime
from ..main import get_db
from ...database.model_db import User

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
SCHEME = os.getenv("SCHEME")



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
        print(f"JWTError occurred: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User timed out due to inactivity, Login to continue")


user_dependency = Annotated[str, Depends(get_user)]
