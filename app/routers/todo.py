from fastapi import APIRouter, HTTPException, Depends, Path
from ..schemas.database import begin, engine 
from ..schemas.model_db import Todo
from ..schemas import model_db as model_db
from starlette import status
from pydantic import BaseModel, Field
from typing import Annotated, Optional
from .user import get_user
from datetime import datetime
from sqlalchemy.orm import Session

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
db_dependency = Annotated[Session, Depends(get_db)]
user_dependancy = Annotated[str, Depends(get_user)]

#Todo create class
class CreateTodo(BaseModel):
    tasks : Annotated[str, Field(max_length= 100)]
    completed : Annotated[bool, Field(Optional)]
    note : Annotated[str, Field(max_length= 100)]
    due : Annotated[str, Field()]
    
    class Config():
        json_schema_extra = {
            'example' : {
                "tasks" : "task",
                "note" : "note",
                "due" : "Monday"
            }
        }

#Update Todo details class
class UpdateTodo(BaseModel):
    tasks : Annotated[str, Field(max_length= 100)]
    completed : Annotated[bool, Field(Optional)]
    note : Annotated[str, Field(max_length= 100)]
    due : Annotated[str, Field]
    user_id : Annotated[int, Field(Optional)]

    class Config():
        json_schema_extra = {
            'example' : {
                "tasks" : "task",
                "note" : "note",
                "due" : 'Monday'
            }
        }


#get all tasks route
@todo.get("/all-todo", status_code= status.HTTP_200_OK, response_description= {200 : {"description" : "User has requested for all todo that is present"}})
async def get_all_todo(user : user_dependancy,db : db_dependency):
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Unauthorized User")
    
    data = db.query(Todo).filter(Todo.user_id == user.get("user_id")).all()
    if not data:
        pass

    return data


#get tasks by id route
@todo.get("/get-todo/{todo_id}", status_code= status.HTTP_200_OK, response_description= {200 : {"description" : "User has searched for todo based on todo id"}})
async def get_todo_by_id(user : user_dependancy, db : db_dependency, todo_id : int = Path(gt= 0)):
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Unauthorized user")
    
    data = db.query(Todo).filter(Todo.user_id == user.get("user_id")).filter(Todo.id == todo_id).first()

    if data is not None:
        return data
    
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Todo not found")


#get tasks by title route
@todo.get("/get-todo/u/{todo_name}", status_code= status.HTTP_200_OK, response_description= {200 : {"description" : "User has searched for todo based on todo name"}})
async def get_todo_by_name(user : user_dependancy, db : db_dependency, todo_name : str = Path(max_length= 100)):
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Unauthorized user")
    
    data = db.query(Todo).filter(Todo.user_id == user.get("user_id")).filter(Todo.task == todo_name).all()

    if data is not None:
        return data
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "Todo not found")


#get tasks by completed route
@todo.get("/get-todo/u/1/{completed}",status_code= status.HTTP_200_OK, response_description= {200 : {"description" : "User has searched for todo based on completed or not completed todo"}})
async def get_todo_by_completed(user : user_dependancy, db : db_dependency, completed : bool):
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Unauthorized user")
    
    data = db.query(Todo).filter(Todo.user_id == user.get("user_id")).filter(Todo.completed == completed).all()
    
    if data is not None:
        return data
    
    raise HTTPException(status_code= status.HTTP_422_UNPROCESSABLE_ENTITY, detail= "Invalid Parameters")


#create tasks route
@todo.post("/create-todo",status_code= status.HTTP_201_CREATED, response_description= {201 : {"description" : "User has successfully created a todo"}})
async def create_todo(user : user_dependancy, db : db_dependency, form : CreateTodo):
    todo_created = False
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Unauthorized user")
    
    data = Todo(
        task = form.tasks,
        completed = False,
        note = form.note,
        due = form.due,
        user_id = user.get("user_id")
    )

    todo_created = True

    if todo_created is not True:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "Bad Request, Please try again later")
    
    db.add(data)
    db.commit()
    db.refresh(data)


#update tasks route to be complete   
@todo.put("/update-todo/complete-todo/{todo_id}",status_code= status.HTTP_202_ACCEPTED, response_description= {202 : {"description" : "User has marked todo to be completed"}})
async def update_todo_to_be_true(user : user_dependancy, db : db_dependency, complete : bool, todo_id : int = Path(gt=0)):
    todo_completed = False
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Unauthorized user")
    
    todo_update = db.query(Todo).filter(Todo.user_id == user.get("user_id")).filter(Todo.id == todo_id).first()
    if todo_update is None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Todo not found")
    
    todo_update.completed = complete

    todo_completed = True
    if todo_completed is not True:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= "Bad Request, Please try again later")
    
    db.add(todo_update)
    db.commit()
    db.refresh(todo_update)


#update tasks route to update other details 
@todo.put("/update-todo/details/{todo_id}", status_code= status.HTTP_202_ACCEPTED, responses= {200: {"description" : "User has updated the todo details based on todo id "}})
async def update_todo(user : user_dependancy, db : db_dependency, form : UpdateTodo, todo_id : int =Path(gt=0)):
    todo_updated = False
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Unauthorized user")
    
    todo_data = db.query(Todo).filter(Todo.user_id == user.get("user_id")).filter(Todo.id == todo_id).first()

    if todo_data is None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Todo not found")
    
    todo_data.task = form.tasks
    todo_data.note = form.note
    todo_data.due = form.due
        
    todo_updated = True
    if todo_updated is not True:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= "Bad Request, Please try again later")
    
    db.add(todo_data)
    db.commit()
    db.refresh(todo_data)


#delete tasks route
@todo.delete("/delete-todo/{todo_id}",status_code= status.HTTP_204_NO_CONTENT, response_description= {204 : {"description" : "User has deleted a todo based off of todo id"}})
async def delete_single_task(user : user_dependancy, db : db_dependency, todo_id : int = Path(gt=0)):
    delete_todo = False
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Unauthorized user")
    
    todo_delete = db.query(Todo).filter(Todo.user_id == user.get("user_id")).filter(Todo.id == todo_id).first()

    if todo_delete is None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,detail= "Todo not found")
    
    delete_todo = True
    if delete_todo is not True:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "Bad Request, Please try again later")

    db.delete(todo_delete)
    db.commit()


#delete tasks route with completed todo
@todo.delete("/delete/all/{completed_todo}", status_code= status.HTTP_204_NO_CONTENT, response_description= {204 : {"description" : "User has deleted all todo that has been completed "}})
async def delete_all_completed_tasks(user : user_dependancy, db : db_dependency, completed_todo : bool = Path()):
    delete_todos = False
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Unauthorized user")
    
    data = db.query(Todo).filter(Todo.user_id == user.get("user_id")).filter(Todo.completed == completed_todo).all()

    if data is None:
        raise HTTPException(status_code= status.HTTP_422_UNPROCESSABLE_ENTITY, detail= "Invalid Credentials")
    
    db.query(Todo).filter(Todo.user_id == user.get("user_id")).filter(Todo.completed == completed_todo).delete()
    delete_todos = True
    if delete_todos is not True:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "No Todo available")
    
    
    db.commit()
