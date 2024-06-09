from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.schemas.database import data
from app.schemas.model_db import Todo, User
import pytest
from app.main import app
from fastapi.testclient import TestClient
from app.routers.user import hash


database = "sqlite:///testdb.sqlite"
engine = create_engine(
    database, 
    connect_args= {"check_same_thread" : False},
    poolclass= StaticPool
)

test_begin =sessionmaker(bind= engine, autocommit = False, autoflush = False)
data.metadata.create_all(bind= engine)

def overide_get_db():
    db = test_begin()
    try:
        yield db

    finally:
        db.close

def overide_get_user():
    return {"username" : "Imisioluwa23", "user_id" : 1} 

client = TestClient(app)

@pytest.fixture
def test_todo():
    todo = Todo(
        id =1,
        task = "Trying to test out my todo test",
        completed = False,
        note = "This is kinda getting boring, Front-end sucks",
        due = "Today",
        user_id = 1,
    )

    db = test_begin()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM 'Todo';"))
        connection.commit()


@pytest.fixture
def test_user():
    user = User(
        id = 1,
        firstname = "Imisioluwa",
        lastname = "Isong",
        username = "Imisioluwa23",
        email = "isongrichard234@gmail.com",
        password = hash.hashed("Interstellar.")
    )

    db =test_begin()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM 'User';"))
        connection.commit()
