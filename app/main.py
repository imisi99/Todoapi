from fastapi import FastAPI
from .routers.todo import todo
from .routers.user import user
from .schemas.database import engine
from .schemas import model_db as model_db


app = FastAPI()
app.include_router(user, prefix="/user", tags=["User"])
app.include_router(todo, prefix="/todo", tags=["Todo"])


@app.get("/")
async def landing_page():
    return "Create your To Do tasks with us today, click here to login/signup"

model_db.data.metadata.create_all(bind=engine)
