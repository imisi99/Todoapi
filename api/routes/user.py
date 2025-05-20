import uuid
import json
from fastapi import APIRouter, HTTPException
from starlette import status
from datetime import timedelta
from ..config import hashed, db_dependency, authentication, authorization, user_dependency, otp_authentication, otp_token_verification, otp_dependency
from schema.user_schema import SignupForm, LoginForm, Token, UserDetails, UpdateUser, NewPassword, ForgotPassowrd, OTPGeneration, OTPVerification, DeleteUser
from database.model_db import Todo, User, Otp


user = APIRouter()



@user.post("/signup", status_code=status.HTTP_201_CREATED)
async def user_signup(payload: SignupForm, db: db_dependency):
    existing_username = db.query(User).filter(User.username == payload.username).first()
    existing_email = db.query(User).filter(User.email == payload.email).first()
    
    if existing_email and existing_username:
        raise HTTPException(status_code=status.HTTP_226_IM_USED, detail="username and email already in use!")
    elif existing_username:
        raise HTTPException(status_code=status.HTTP_226_IM_USED, detail="username is already in use!")
    elif existing_email:
        raise HTTPException(status_code=status.HTTP_226_IM_USED, detail="email is already in use!")

    user = User(
        id=str(uuid.uuid4()),
        firstname=payload.firstname,
        lastname=payload.lastname,
        username=payload.username,
        email=payload.email,
        password=hashed.hash(payload.password)

    )
    

    db.add(user)
    db.commit()
    db.refresh(user)

    return json.dumps({"message": "User Signed up sucessfully"})



@user.post("/login", status_code=status.HTTP_202_ACCEPTED)
async def user_login(payload: LoginForm, db: db_dependency):
    user = authorization(payload.username, payload.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    token = authentication(user.role, user.id, timedelta(hours=1))

    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error trying to log you in please try again later")

    return json.dumps(Token(
        access_token=token,
        token_type="bearer"
    ).dict())



@user.get("/get-user-details", status_code=status.HTTP_200_OK)
async def get_current_user_details(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    user_data = db.query(User).filter(User.id == user.get("user_id")).first()

    if not user_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to fetch user info")

    userDetails = UserDetails(
        firstname=user_data.firstname,
        lastname=user_data.lastname,
        username=user_data.username
        email=user_data.email
    )
    
    return json.dumps(userDetails.dict())



@user.put("/update-user-details", status_code=status.HTTP_202_ACCEPTED)
async def update_user_details(user: user_dependency, payload: UpdateUser, db: db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    user_details = db.query(User).filter(User.id == user.get("user_id")).first()

    existing_email = db.query(User).filter(User.email == payload.email).first()
    existing_username = db.query(User).filter(User.username == payload.username).first()

    if existing_email is not None and existing_email.email != user_details.email:
        raise HTTPException(status_code=status.HTTP_226_IM_USED, detail="email is already in use")

    if existing_username is not None and existing_username.username != user1.username:
        raise HTTPException(status_code=status.HTTP_226_IM_USED, detail="username is already in use")

    user1.firstname = payload.firstname
    user1.lastname = payload.lastname
    user1.email = payload.email
    user1.username = payload.username


    db.add(user_details)
    db.commit()
    db.refresh(user_details)

    return json.dumps({"message": "User details has been updated successfully."})



@user.put("/update-user-password", status_code=status.HTTP_202_ACCEPTED)
async def change_user_password(user: user_dependency, payload: NewPassword, db: db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    user_details = db.query(User).filter(User.id == user.get("user_id")).first()

    if not user_details:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to fetch user details")

    password = hashed.verify(payload.password, user_details.password)
    if not password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Password!")

    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password does not match")

    user_details.password = hashed.hash(payload.new_password)


    db.add(user_details)
    db.commit()
    db.refresh(user_details)
    
    updated_password_email(user_details.email)

    return json.dumps({"message": "Password has been updated successfully"})



@user.get("/generate-otp", status_code=status.HTTP_200_OK)
async def user_forgot_password(db: db_dependency, payload: OTPGeneration):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found!")

    otp = generate_otp()
    
    otp_obj = Otp(
        otp=otp,
        user_id=user.id
    )
    
    otp_generation_email(user.email, otp)

    db.add(otp_obj)
    db.commit()
    db.refresh(otp_obj)
    
    return json.dumps({"message": "Email sent successfully"})



@user.get("/verify-otp", status_code=status.HTTP_200_OK)
async def verify_otp(db: db_dependency, payload: OTPVerification):
    otp = db.query(Otp).filter(Otp.otp == payload.otp).first()
    if otp.expiring > datetime.now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Expired otp!")
    
    if not otp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid otp!")
    
    token = otp_authentication(otp.user_id)
    
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="An error occured while validating otp")
    
    return json.dumps({"token": token})
    
    
    
@user.put("/change-user-password", status_code=status.HTTP_202_ACCEPTED)
async def change_user_password(db: db_dependency, otp: otp_dependency, payload: ForgotPassword):
    if not otp:
        raise HTTPException(status_code=status.HTTP_401_AUTHORIZED, detail="Invalid session token")
    
    user = db.query(User).filter(User.id == opt.get("user_id")).first()
    
    hashed_password = hashed.hash(payload.new_password)
    
    user.password = hashed_password
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return json.dumps({"message": "Password Changed Successfully"})



@user.delete("/delete-user", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: user_dependency, db: db_dependency, payload: DeleteUser):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    user_details = db.query(User).filter(User.id == user.get("user_id")).first()
    todo = db.query(Todo).filter(Todo.user_id == user.get("user_id")).delete()

    if not user_details:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error while deleting user data")

    if user_details.username != payload.username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    db.delete(delete)
    db.commit()

    return json.dumps({"message": "User data has been deleted successfully"})
