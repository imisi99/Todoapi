from .database import data
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, ForeignKey, Boolean, String, DateTime, func


def additional_time():
    return datetime.now() + timedelta(days=1)


def otp_addtional_time():
    return datetime.now() + timedelta(minutes=20)


class User(data):

    __tablename__ = "User"

    id = Column(String, primary_key=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    username = Column(String(20), unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    timezone = Column(String, nullable=False, default="UTC")
    created_at = Column(DateTime, nullable=False, default=func.now())
    role = Column(String(10), nullable=False, default="user")



class Todo(data):

    __tablename__ = "Todo"

    id = Column(Integer, primary_key=True, index=True)
    task = Column(String(50), nullable=False)
    note = Column(String(50), nullable=True)
    completed = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    due = Column(DateTime, nullable=False, default=additional_time())
    user_id = Column(String, ForeignKey("User.id"))



class Otp(data):
    
    __tablename__ = "Otp"
    
    id = Column(Integer, primary_key=True, index=True)
    otp = Column(Integer, nullable=False)
    expiring = Column(DateTime, nullable=False, default=otp_additional_time())
    user_id = Column(String, ForeignKey("User.id"))