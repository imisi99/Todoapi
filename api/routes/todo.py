import json
from fastapi import APIRouter, HTTPException, Path
from starlette import status
from schema.todo_schema import CreateTodo, UpdateTodo
from ..config import db_dependency, user_dependency
from database.model_db import Todo

todo = APIRouter()



@todo.get("/get-todo/all", status_code=status.HTTP_200_OK,)
async def get_all_task(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")

    data = db.query(Todo).filter(Todo.user_id == user.get("user_id")).all()

    if data is not None:
        return json.dumps(data)



@todo.get("/get-todo/id/{todo_id}", status_code=status.HTTP_200_OK)
async def get_task_by_id(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    data = db.query(Todo).filter(Todo.user_id == user.get("user_id")).filter(Todo.id == todo_id).first()

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return json.dumps(data)



@todo.get("/get-todo/name/{todo_name}", status_code=status.HTTP_200_OK)
async def get_task_by_name(user: user_dependency, db: db_dependency, todo_name: str = Path(max_length=55)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    data = db.query(Todo).filter(Todo.user_id == user.get("user_id")).filter(Todo.task == todo_name).all()

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return json.dumps(data)



@todo.get("/get-todo/status/{completed}", status_code=status.HTTP_200_OK)
async def get_task_by_status(user: user_dependency, db: db_dependency, completed: bool):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    data = db.query(Todo).filter(Todo.user_id == user.get("user_id")).filter(Todo.completed == completed).all()

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return json.dumps(data)



@todo.post("/create-todo", status_code=status.HTTP_201_CREATED)
async def create_task(user: user_dependency, db: db_dependency, payload: CreateTodo):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    todo = Todo(
        task=payload.tasks,
        note=payload.note,
        user_id=user.get("user_id")
    )

    db.add(todo)
    db.commit()
    db.refresh(todo)



@todo.put("/update-todo/complete-todo/{todo_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_task_status(user: user_dependency, db: db_dependency, status: bool, todo_id: int = Path(gt=0)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    task = db.query(Todo).filter(Todo.user_id == user.get("user_id")).filter(Todo.id == todo_id).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    task.completed = status

    db.add(todo_update)
    db.commit()
    db.refresh(todo_update)



@todo.put("/update-todo/details/{todo_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_todo(user: user_dependency, db: db_dependency, payload: UpdateTodo, todo_id: int = Path(gt=0)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    task = db.query(Todo).filter(Todo.user_id == user.get("user_id")).filter(Todo.id == todo_id).first()

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    task.task = payload.tasks
    task.note = payload.note
    task.status = payload.status
    task.due = payload.due

    db.add(todo_data)
    db.commit()
    db.refresh(todo_data)


# Delete tasks router
@todo.delete("/delete-todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT,
             response_description={204: {"description": "User has deleted a todo based off of todo id"}})
async def delete_single_task(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    delete_todo = False
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    todo_delete = db.query(Todo).filter(Todo.user_id == user.get("user_id")).filter(Todo.id == todo_id).first()

    if todo_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    delete_todo = True
    if delete_todo is not True:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request, Please try again later")

    db.delete(todo_delete)
    db.commit()


# Delete tasks router with completed todo
@todo.delete("/delete/all/{completed_todo}", status_code=status.HTTP_204_NO_CONTENT,
             response_description={204: {"description": "User has deleted all todo that has been completed "}})
async def delete_all_completed_tasks(user: user_dependency, db: db_dependency, completed_todo: bool = Path()):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    data = db.query(Todo).filter(Todo.user_id == user.get("user_id")).filter(Todo.completed == completed_todo).all()

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Todo available")

    db.query(Todo).filter(Todo.user_id == user.get("user_id")).filter(Todo.completed == completed_todo).delete()

    db.commit()
