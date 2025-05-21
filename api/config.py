import os
import smtplib
import random
from fastapi import Depends, HTTPException
from starlette import status
from typing import Annotated
from passlib.context import CryptContext
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
from database.database import begin
from database.model_db import User
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
SCHEME = os.getenv("SCHEME")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")


def get_db():
    db = begin()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

hashed = CryptContext(schemes=[SCHEME])


def authorization(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    password = hashed.verify(password, user.password)
    if not password:
        return False
    return user


SECRET = SECRET_KEY

Algorithm = ALGORITHM


def authentication(role: str, user_id: str, expiring):
    encode = {'sub': role, 'id': user_id}
    expired = datetime.now() + expiring
    encode.update({'exp': expired})
    return jwt.encode(encode, SECRET, algorithm=Algorithm)


bearer = OAuth2PasswordBearer(tokenUrl="user/login")
otp_bearer = OAuth2PasswordBearer(tokenUrl="user/verify-otp")


async def get_user(token: Annotated[str, Depends(bearer)]):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[Algorithm])
        role: str = payload.get("sub")
        user_id: int = payload.get("id")
        if role is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
        return {
            "role": role,
            "user_id": user_id
        }

    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Timeout session expired!")


def otp_authentication(user_id: str):
    encode = {'id': user_id}
    expiring = datetime.now() + timedelta(minutes=15)
    encode.update({'exp': expiring})
    return jwt.encode(encode, SECRET, algorithm=Algorithm)


async def otp_token_verification(token: Annotated[str, Depends(otp_bearer)]):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[Algorithm])
        user_id: int = payload.get("id")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
        return {"user_id": user_id}
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_400_UNAUTHORIZED, detail="Timeout session expired!")
    

def send_email(user_email, subject, body):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["Subject"] = subject
    
    message.attach(MIMEText(body, "html"))
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            
            message["To"] = user_email
            server.sendmail(SENDER_EMAIL, user_email, message.as_string())
    except smtplib.SMTPEcxeption as e:
        return "An error occured while trying to send an email"


def signup_email(user_email, username):
    subject = "Welcome to Sodot"
    body = f'''
    <div style="font-family: Arial, sans-serif; color: #333; background-color: #f0f4f8; padding: 20px; border-radius: 10px; text-align: center;">
        <h3 style="color: #4caf50;">Hey {username}, Welcome Aboard! 🎉</h3>
        <p style="font-size: 15px;">
            We're thrilled to have you with us. <strong>Sodot</strong> is your new sidekick for staying organized and getting things done without the stress.
        </p>
        <p style="font-size: 15px; margin-top: 10px;">
            Your space to plan smarter, prioritize better, and actually enjoy crossing things off that list.
            Let's turn chaos into clarity - one task at a time, one win at a time.
        </p>
        <div style="margin-top: 20px;">
            <a href="https://link.com" style="text-decoration: none; background-color: #4caf50; color: white; padding: 10px 20px; border-radius: 5px; font-size: 15px;">Start crossing it off ✔️</a>
        </div>
        <p style="font-size: 14px; color: #757575; margin-top: 20px;">
            You've got this 💪,<br/>
            <strong>The Sodot Team</strong>
        </p>
    </div>
    '''
    send_email(user_email, subject, body)
    

def otp_email(user_email, username, otp):
    subject = "Your Sodot OTP Code"
    body = f'''
    <div style="font-family: Arial, sans-serif; color: #333; background-color: #f9f9f9; padding: 20px; border-radius: 8px; text-align: center;">
        <h2 style="color: #4caf50;">Hi {username},</h2>
        <p style="font-size: 16px;">
            <em>Oops! We heard you've lost your password.</em><br/>
            But don't worry! We've got your back. 
        </p>
        <p style="font-size: 16px;">
            <strong>Use the following OTP to reset your password it is valid for 20 minutes</strong>
        </p>
        <div style="text-align: center; margin: 20px 0;">
            <span style="font-size: 24px; font-weight: bold; color: #4caf50; background-color: #e8f5e9; padding: 10px 20px; border-radius: 4px; display: inline-block;">{otp}</span>
        </div>
        <p style="font-size: 14px; color: #757575;">
            If you didn’t request a password reset, no worries—your account is safe and sound!
        </p>
        <p style="font-size: 14px; color: #757575;">
            Cheers,<br/>
            <strong>The Sodot Team</strong>
        </p>
    </div>
    '''
    send_email(user_email, subject, body)
    
    
def password_email(user_email, username):
    subject = "Your Sodot Password Was Changed"
    body = f'''
    <div style="font-family: Arial, sans-serif; color: #333; background-color: #fff5f5; padding: 20px; border-radius: 10px; text-align: center;">
        <h3 style="color: #e53935;">Hey {username}, your password was updated 🔒</h3>
        <p style="font-size: 15px;">
            Just a heads-up that your Sodot password was recently changed.
        </p>
        <p style="font-size: 15px; margin-top: 10px;">
            If this was you, you're all set. If not, please reset your password immediately.
        </p>
        <div style="margin-top: 20px;">
            <a href="https://link-to-reset.com" style="text-decoration: none; background-color: #e53935; color: white; padding: 10px 20px; border-radius: 5px; font-size: 15px;">Reset Password</a>
        </div>
        <p style="font-size: 14px; color: #757575; margin-top: 20px;">
            Stay safe,<br/>
            <strong>The Sodot Team</strong>
        </p>
    </div>
    '''
    send_email(user_email, subject, body)
    
    
def delete_email(user_email, username, otp):
    subject = "Sodot Account Deletion"
    body = f'''
        <div style="font-family: Arial, sans-serif; color: #333; background-color: #f9f9f9; padding: 20px; border-radius: 8px; text-align: center;">
            <h2 style="color: #ff6b6b;">Hi {username},</h2>
            <p style="font-size: 16px;">
                <em>We've received a request to delete your account.</em><br/>
                We are sad to see you go 😭
            </p>
            <p style="font-size: 16px;">
                <strong>Please use the OTP below to confirm account deletion. It's valid for 20 minutes</strong>
            </p>
            <div style="text-align: center; margin: 20px 0;">
            <span style="font-size: 24px; font-weight: bold; color: #4caf50; background-color: #e8f5e9; padding: 10px 20px; border-radius: 4px; display: inline-block;">{otp}</span>
            </div>
            <p style="font-size: 14px; color: #757575;">
            If you didn’t request this, no worries—your account is safe and sound!
            </p>
            <p style="font-size: 14px; color: #757575;">
                Thank you for being part of our journey,<br/>
                <strong>Sodot Team</strong>
            </p>
        </div>
    '''
    send_email(user_email, subject, body)


def generate_otp():
    otp = random.randint(100000, 999999)
    return str(otp)


otp_dependency = Annotated[dict, Depends(otp_token_verification)]
user_dependency = Annotated[str, Depends(get_user)]
