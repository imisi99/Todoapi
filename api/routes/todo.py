from fastapi import APIRouter, HTTPException, Path
from starlette import status
from schema.todo_schema import CreateTodo, UpdateTodo
from ..config import db_dependency, user_dependency
from database.model_db import Todo

todo = APIRouter()



# Get all tasks router
@todo.get("/all-todo", status_code=status.HTTP_200_OK,
          response_description={200: {"description": "User has requested for all todo that is present"}})
async def get_all_todo(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")

    data = db.query(Todo).filter(Todo.user_id == user.get("user_id")).all()
    if not data:
        pass

    return data


# Get tasks by id router
@todo.get("/get-todo/{todo_id}", status_code=status.HTTP_200_OK,
          response_description={200: {"description": "User has searched for todo based on todo id"}})
async def get_todo_by_id(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    data = db.query(Todo).filter(Todo.user_id == user.get("user_id")).filter(Todo.id == todo_id).first()

    if data is not None:
        return data

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")


# Get tasks by title router
@todo.get("/get-todo/u/{todo_name}", status_code=status.HTTP_200_OK,
          response_description={200: {"description": "User has searched for todo based on todo name"}})
async def get_todo_by_name(user: user_dependency, db: db_dependency, todo_name: str = Path(max_length=100)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    data = db.query(Todo).filter(Todo.user_id == user.get("user_id")).filter(Todo.task == todo_name).all()

    if data is not None:
        return data

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")


# Get tasks by completed router
@todo.get("/get-todo/u/1/{completed}", status_code=status.HTTP_200_OK, response_description={
    200: {"description": "User has searched for todo based on completed or not completed todo"}})
async def get_todo_by_completed(user: user_dependency, db: db_dependency, completed: bool):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    data = db.query(Todo).filter(Todo.user_id == user.get("user_id")).filter(Todo.completed == completed).all()

    if data is not None:
        return data

    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid Parameters")



@todo.post("/create-todo", status_code=status.HTTP_201_CREATED,
           response_description={201: {"description": "User has successfully created a todo"}})
async def create_todo(user: user_dependency, db: db_dependency, form: CreateTodo):
    todo_created = False
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    data = Todo(
        task=form.tasks,
        completed=False,
        note=form.note,
        due=form.due,
        user_id=user.get("user_id")
    )

    todo_created = True

    if todo_created is not True:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request, Please try again later")

    db.add(data)
    db.commit()
    db.refresh(data)


# Update tasks router to be complete
@todo.put("/update-todo/complete-todo/{todo_id}", status_code=status.HTTP_202_ACCEPTED,
          response_description={202: {"description": "User has marked todo to be completed"}})
async def update_todo_to_be_true(user: user_dependency, db: db_dependency, complete: bool, todo_id: int = Path(gt=0)):
    todo_completed = False
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    todo_update = db.query(Todo).filter(Todo.user_id == user.get("user_id")).filter(Todo.id == todo_id).first()
    if todo_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    todo_update.completed = complete

    todo_completed = True
    if todo_completed is not True:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request, Please try again later")

    db.add(todo_update)
    db.commit()
    db.refresh(todo_update)


# Update tasks router to update other details
@todo.put("/update-todo/details/{todo_id}", status_code=status.HTTP_202_ACCEPTED,
          responses={200: {"description": "User has updated the todo details based on todo id "}})
async def update_todo(user: user_dependency, db: db_dependency, form: UpdateTodo, todo_id: int = Path(gt=0)):
    todo_updated = False
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    todo_data = db.query(Todo).filter(Todo.user_id == user.get("user_id")).filter(Todo.id == todo_id).first()

    if todo_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    todo_data.task = form.tasks
    todo_data.note = form.note
    todo_data.due = form.due

    todo_updated = True
    if todo_updated is not True:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request, Please try again later")

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
