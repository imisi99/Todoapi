import uuid
from fastapi import APIRouter, HTTPException
from starlette import status
from datetime import timedelta
from .config import hashed, db_dependency, authentication, authorization, user_dependency
from ...schema.user_schema import SignupForm, LoginForm, Token, UserDetails, UpdateUser, NewPassword, ForgotPassowrd
from ...database.model_db import Todo, User


user = APIRouter()


@user.post("/signup", status_code=status.HTTP_201_CREATED,
           response_description={201: {"description": "User has successfully signed up"}})
async def user_signup(userpayload: SignupForm, db: db_dependency):
    signup = False
    existing_username = db.query(User).filter(User.username == userpayload.username).first()
    existing_email = db.query(User).filter(User.email == userpayload.email).first()
    if existing_email and existing_username:
        raise HTTPException(status_code=status.HTTP_226_IM_USED, detail="username and email already in use!")
    if existing_username:
        raise HTTPException(status_code=status.HTTP_226_IM_USED, detail="username is already in use!")

    if existing_email:
        raise HTTPException(status_code=status.HTTP_226_IM_USED, detail="email is already in use!")

    user = User(
        id=str(uuid.uuid4()),
        firstname=userpayload.firstname,
        lastname=userpayload.lastname,
        username=userpayload.username,
        email=userpayload.email,
        password=hashed.hash(userpayload.password)

    )
    signup = True

    if signup is not True:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error in trying to validate user")

    db.add(user)
    db.commit()
    db.refresh(user)

    return "User has been created successfully"


# User login router
@user.post("/login", response_model=Token, status_code=status.HTTP_202_ACCEPTED,
           response_description={202: {"description": "User has logged in successfully"}})
async def user_login(payload: LoginForm, db: db_dependency):
    user = authorization(payload.username, payload.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    token = authentication(user.role, user.id, timedelta(hours=1))

    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error trying to log you in please try again later")

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# Get logged-in user details router
@user.get("/get-user-details", status_code=status.HTTP_200_OK,
          response_description={200: {"description": "Logged in user has successfully received details"}})
async def get_current_user_details(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    user_data = db.query(User).filter(User.id == user.get("user_id")).first()

    if user_data is not None:
        data = UserDetails(
            firstname=user_data.firstname,
            lastname=user_data.lastname,
            email=user_data.email,
            username=user_data.username,
        )

        return data

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Error in getting user details, please try again later")


# User update details router
@user.put("/update-user-details", status_code=status.HTTP_202_ACCEPTED,
          response_description={202: {"description": "User details have been updated successfully"}})
async def update_user_details(user: user_dependency, payload: UpdateUser, db: db_dependency):
    user_update = False
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    user1 = db.query(User).filter(User.id == user.get("user_id")).first()

    existing_email = db.query(User).filter(User.email == payload.email).first()
    existing_username = db.query(User).filter(User.username == payload.username).first()

    if existing_email is not None and existing_email.email != user1.email:
        raise HTTPException(status_code=status.HTTP_226_IM_USED, detail="email is already in use")

    if existing_username is not None and existing_username.username != user1.username:
        raise HTTPException(status_code=status.HTTP_226_IM_USED, detail="username is already in use")

    if user1 is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid login credentials")

    user1.firstname = payload.firstname
    user1.lastname = payload.lastname
    user1.email = payload.email
    user1.username = payload.username

    user_update = True

    if user_update is not True:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="An error occurred while trying to update user, please try again later")

    db.add(user1)
    db.commit()
    db.refresh(user1)

    return "User details have been Updated successfully"


# User changes password router
@user.put("/change-user-password", status_code=status.HTTP_202_ACCEPTED,
          response_description={202: {"description": "User password has been changed successfully"}})
async def change_user_password(user: user_dependency, payload: NewPassword, db: db_dependency):
    password_changed = False
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    user1 = db.query(User).filter(User.id == user.get("user_id")).first()

    if not user1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid login credentials")

    password = hashed.verify(payload.password, user1.password)
    if not password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Password! ")

    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password does not match")

    user1.password = hashed.hash(payload.new_password)

    password_changed = True

    if password_changed is not True:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error while trying to process new password, please try again later")

    db.add(user1)
    db.commit()
    db.refresh(user1)

    return "Password has been Changed Successfully"



@user.put("/forgot-password", status_code=status.HTTP_202_ACCEPTED,
          response_description={202: {"description": "User has successfully changed password"}})
async def user_forgot_password(db: db_dependency, payload: ForgotPassowrd):
    password_changed = False
    user = db.query(User).filter(User.username == payload.username).filter(User.email == payload.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid user credentials!")

    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password does not match")

    user.password = hashed.hash(payload.new_password)

    password_changed = True

    if password_changed is not True:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error while trying to process new password, please try again later")

    db.add(user)
    db.commit()
    db.refresh(user)

    return "User password has been updated successfully"


# User delete router
@user.delete("/delete-user", status_code=status.HTTP_204_NO_CONTENT,
             response_description={204: {"description": "User details alongside todos has been deleted successfully"}})
async def delete_user(user: user_dependency, db: db_dependency):
    user_deleted = False
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    delete = db.query(User).filter(User.id == user.get("user_id")).first()
    todo = db.query(Todo).filter(Todo.user_id == user.get("user_id")).delete()

    if not delete:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error while deleting user data")

    if not todo:
        pass

    user_deleted = True

    if user_deleted is not True:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error while deleting user, please try again later")

    db.delete(delete)
    db.commit()

    return "User has been deleted successfully"
