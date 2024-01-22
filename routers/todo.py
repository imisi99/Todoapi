from fastapi import APIRouter, HTTPException, Depends
from schemas.database import begin, engine 
from schemas.model_db import Todo
import schemas.model_db as model_db
from starlette import status
from pydantic import BaseModel, Field
from typing import Annotated
from .user import get_user

todo = APIRouter()

#Getting the sessionmaker from the database and creating the DB
model_db.data.metadata.create_all(bind = engine)

#Initializinig the database to be able to write data to it 
def get_db():
    db = begin()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[str, Depends(get_db)]
user_dependancy = Annotated[str, Depends(get_user)]



