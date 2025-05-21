import uuid
import json
from fastapi import APIRouter, HTTPException
from starlette import status
from datetime import timedelta
from ..config import hashed, db_dependency, authentication, authorization, user_dependency, otp_authentication, otp_token_verification, otp_dependency, otp_email, password_email, signup_email, delete_email, generate_otp
from schema.user_schema import SignupForm, LoginForm, Token, UserDetails, UpdateUser, NewPassword, ForgotPassowrd, OTPGeneration, OTPVerification
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

    signup_email(user.email, user.username)
    
    return json.dumps({"message": "User Signed up sucessfully"})



@user.post("/login", status_code=status.HTTP_202_ACCEPTED)
async def user_login(payload: LoginForm, db: db_dependency):
    user = authorization(payload.username, payload.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password!")

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

    user_details.firstname = payload.firstname
    user_details.lastname = payload.lastname
    user_details.email = payload.email
    user_details.username = payload.username


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
    
    password_email(user_details.email, user_details.username)

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
    
    otp_email(user.email, user.username, otp)

    db.add(otp_obj)
    db.commit()
    db.refresh(otp_obj)
    
    return json.dumps({"message": "Email sent successfully"})



@user.get("/verify-otp", status_code=status.HTTP_200_OK)
async def verify_otp(db: db_dependency, payload: OTPVerification):
    otp = db.query(Otp).filter(Otp.otp == payload.otp).first()
    
    if not otp or otp.tag != "Password":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid otp!")
    
    if otp.expiring > datetime.now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Expired otp!")
    
    if otp.is_used:
        raised HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Used otp!")
    
    
    token = otp_authentication(otp.user_id)
    
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="An error occured while validating otp")
    
    otp.is_used = True
    
    db.add(otp)
    db.commit()
    db.refresh(otp)
    
    return json.dumps({"token": token})
    
    
    
@user.put("/change-user-password", status_code=status.HTTP_202_ACCEPTED)
async def change_user_password(db: db_dependency, otp: otp_dependency, payload: ForgotPassword):
    if not otp:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session token")
    
    user = db.query(User).filter(User.id == otp.get("user_id")).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")
    
    hashed_password = hashed.hash(payload.new_password)
    
    user.password = hashed_password
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    password_email(user.email, user.username)
    
    return json.dumps({"message": "Password Changed Successfully"})



@user.get("/delete-user-request", status_code=status.HTTP_200_OK)
async def delete_user_request(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    user_details = db.query(User).filter(User.id == user.get("user_id")).first()
    
    if not user_details:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to fetch user details")
    
    otp = generate_otp()
    
    otp_obj = Otp(
        otp=otp,
        tag="Deletion"
        user_id=user.id
    )
    
    delete_email(user.email, user.username, otp)
    
    db.add(otp_obj)
    db.commit()
    db.refresh(otp_obj)
    
    
@user.delete("/delete-user", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: user_dependency, db: db_dependency, payload: OTPVerification):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    otp = db.query(Otp).filter(Otp.user_id == user.get("user_id")).filter(Otp.otp == payload.otp).first()
    
    if not otp or otp.tag != "Deletion":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid otp!")
    
    if otp.expiring > datetime.now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Expired otp!")
    
    if otp.is_used:
        raised HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Used otp!")
    
    db.query(Todo).filter(Todo.user_id == user.get("user_id")).delete()
    db.query(Otp).filter(Otp.user_id == user.get("user_id")).delete()
    db.query(User).filter(User.id == user.get("user_id")).delete()

    db.commit()
