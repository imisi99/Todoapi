from .utils import *
from starlette import status
from app.routers.todo import get_user, get_db

app.dependency_overrides[get_db] = overide_get_db
app.dependency_overrides[get_user] = overide_get_user


def test_get_all_task(test_todo):
    response = client.get("/todo/all-todo")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": 1,
            "task": "Trying to test out my todo test",
            "completed": False,
            "note": "This is kinda getting boring, Front-end sucks",
            "due": "Today",
            "user_id": 1
        }
    ]


def test_get_task_id(test_todo):
    response = client.get("/todo/get-todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": 1,
        "task": "Trying to test out my todo test",
        "completed": False,
        "note": "This is kinda getting boring, Front-end sucks",
        "due": "Today",
        "user_id": 1
    }


def test_get_task_id_fail(test_todo):
    response = client.get("/todo/get-todo/9")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}


def test_create_todo(test_todo):
    todo_form = {
        "tasks": "Get it done",
        "note": "Getting things",
        "due": "Wednesday",
    }
    response = client.post("/todo/create-todo", json=todo_form)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() is None


def test_update_todo(test_todo):
    response = client.put("/todo/update-todo/complete-todo/1", params={"complete": True})
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() is None


def test_update_todo_fail(test_todo):
    response = client.put("/todo/update-todo/complete-todo/2", params={"complete": True})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}


def test_update_todo_details(test_todo):
    form = {
        "tasks": "Getting things done",
        "note": "Please get things done",
        "due": "Monday"
    }
    response = client.put("/todo/update-todo/details/1", json=form)
    assert response.status_code == status.HTTP_202_ACCEPTED


def test_delete_todo(test_todo):
    response = client.delete("/todo/delete-todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_all_todo(test_todo):
    response = client.delete("/todo/delete/all/True")
    assert response.status_code == status.HTTP_404_NOT_FOUND
