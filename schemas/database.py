from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

database = 'sqlite:///todoapi.sqlite'
engine = create_engine(database, connect_args={"check_same_thread" : False})
begin = sessionmaker(bind = engine, autocommit = False, autoflush = False)
data = declarative_base()