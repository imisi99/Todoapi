from .utils import *
from app.routers.user import get_user, get_db, authorization,authentication, jwt, timedelta, SECRECT, Algorithm
from app.schemas.model_db import User
from starlette import status

app.dependency_overrides[get_db] = overide_get_db
app.dependency_overrides[get_user] = overide_get_user

def test_user_signup(test_user):
    form = {
        "firstname" : "Imisioluwa",
        "lastname" : "Isong",
        "username" : "Imiuwa2345",
        "email" : "isongrichard2@gmail.com",
        "password" : hash.hash("Imisioluwa234.")
    }

    response = client.post("/user/signup", json= form)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == "User has been created successfully"


def test_get_user_details(test_user):
    response = client.get("/user/get-user-details")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "firstname" : "Imisioluwa",
        "lastname" : "Isong", 
        "username" : "Imisioluwa23",
        "email" : "isongrichard234@gmail.com",
    } 

def test_update_user(test_user):
    form = {
        "firstname" : "Imisi",
        "lastname" : "Emma",
        "username" : "Bankai",
        "email" :"isongimisioluwa@gmail.com"
    }
    response = client.put("/user/update-user-details", json= form)
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == "User details have been Updated successfully"


def test_change_user_password(test_user):
    form = {
        "password" : "Interstellar.",
        "new_password" : "Interstellar23.",
        "confirm_password" : "Interstellar23."
    }
    response = client.put("/user/change-user-password",json= form)
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == "Password has been Changed Successfully"

def test_forgot_password(test_user):
    form = {
        "email" : "isongrichard234@gmail.com",
        "username" : "Imisioluwa23",
        "new_password" : "Interstellar.",
        "confirm_password" : "Interstellar."
    }

    response = client.put("/user/forgot-password", json= form)
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == "User password has been updated successfully"

def test_forgot_password_wrong(test_user):
    form = {
        "email" : "isongrichard234@gmail.com",
        "username" : "Imisioluwa23",
        "new_password" : "Interstellar.",
        "confirm_password" : "Interstellar"
    }

    response = client.put("/user/forgot-password", json= form)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {"detail" : "Password does not match"}

def test_delete_user(test_user):
    response = client.delete("/user/delete-user")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_authentication(test_user):
    db =test_begin()

    authenticated = authorization(test_user.username, "Interstellar.", db)
    assert authenticated is not None
    assert authenticated.username == test_user.username

def test_access():
    username = "Imisioluwa23"
    user_id = 1
    expired = timedelta(minutes= 15)

    token = authentication(username, user_id, expired)

    decode = jwt.decode(token, SECRECT, algorithms= Algorithm)

    assert decode['sub'] == username
    assert decode['id'] == user_id

@pytest.mark.asyncio
async def test_get_user(test_user):
    encode = {'sub' : 'Imisioluwa23', 'id' : 1}
    token = jwt.encode(encode, SECRECT, algorithm= Algorithm)

    user = await get_user(token= token)
    assert user == {"username" : "Imisioluwa23", "user_id" : 1}