from .database import data
from sqlalchemy import Column, Integer, ForeignKey, Boolean, String, DateTime

class User(data):

    __tablename__ = "User"

    id = Column(Integer, primary_key= True, index= True)
    first_name = Column(String, nullable= False)
    last_name = Column(String, nullable= False)
    username = Column(String(50), unique= True, nullable= False)
    email = Column(String, nullable= False)
    password = Column(String, nullable=False)


class Todo(data):

    __tablename__ = "Todo"

    id = Column(Integer, primary_key= True, index= True)
    task = Column(String, nullable= False)
    completed = Column(Boolean, nullable= False)
    note = Column(String(50), nullable= True)
    due = Column(DateTime, nullable= False)
    user_id = Column(Integer, ForeignKey("User.id"))