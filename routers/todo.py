from fastapi import APIRouter, HTTPException, Depends
from schemas.database import begin, engine 
from schemas.model_db import Todo
import schemas.model_db as model_db
from starlette import status
from pydantic import BaseModel, Field
from typing import Annotated, Optional
from .user import get_user
from datetime import datetime


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

#Authentication and Authorization
db_dependency = Annotated[str, Depends(get_db)]
user_dependancy = Annotated[str, Depends(get_user)]

#Todo create class
class CreateTodo(BaseModel):
    tasks : Annotated[str, Field(max_length= 100)]
    completed : Annotated[bool, Field(default= False)]
    note : Annotated[str, Field(max_length= 100)]
    due : Annotated[datetime, Field]
    
    class Config():
        json_schema_extra = {
            'example' : {
                "tasks" : "tasks",
                "completed" : False,
                "note" : "note",
                "due" : ""
            }
        }

#Update Todo details class
class UpdateTodo():
    tasks : Annotated[str, Field(max_length= 100)]
    completed : Annotated[bool, Field(default= False)]
    note : Annotated[str, Field(max_length= 100)]
    due : Annotated[datetime, Field]
    user_id : Annotated[int, Field(Optional)]

    class Config():
        json_schema_extra = {
            'example' : {
                "tasks" : "tasks",
                "completed" : False,
                "note" : "note",
                "due" : ""
            }
        }

#Update Todo via completed class
class CompleteTodo():
    completed : Annotated[bool, Field(default=True)]

    class Config():
        json_schema_extra = {
            'example' : {
                "completed" : True
            }
        }

#get all tasks route
#get tasks by id route
#get tasks by title route
#get tasks by completed route
#create tasks route
#update tasks route to be complete
#update tasks route to update other details 
#delete tasks route with tasks name 
#delete tasks route with completed todo

