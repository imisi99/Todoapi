import logging
from fastapi import FastAPI
from routes.todo import todo
from routes.user import user
from ..database.database import engine, begin
from ..database import model_db as model_db
from contextlib import asynccontextmanager


@asynccontextmanager
def lifespan(app: FastAPI):
    model_db.data.metadata.create_all(bind=engine)
    logging.info("Database connection successful")
    yield
    engine.dispose()
    logging.info("Database disposal successful")


app = FastAPI(lifespan=lifespan)
app.include_router(user, prefix="/user", tags=["User"])
app.include_router(todo, prefix="/todo", tags=["Todo"])


@app.get("/")
async def landing_page():
    return "Create your To Do tasks with us today, click here to login/signup"


def get_db():
    db = begin()
    try:
        yield db
    finally:
        db.close()
        