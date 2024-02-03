from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

database = 'postgresql://postgres:Imisioluwa234.@localhost/Todoapi'
engine = create_engine(database)
begin = sessionmaker(bind = engine, autocommit = False, autoflush = False)
data = declarative_base()
