import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base


DATABASE_URL = os.getenv("DATABASE_URL")
database = DATABASE_URL
engine = create_engine(database)
begin = sessionmaker(bind=engine, autocommit=False, autoflush=False)
data = declarative_base()
