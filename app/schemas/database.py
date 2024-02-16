from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

database = 'postgresql://ffivcxms:OwG3mL4x_u-T9HLC3Q8Axn8mCCPTmBgP@trumpet.db.elephantsql.com/ffivcxms'
engine = create_engine(database)
begin = sessionmaker(bind = engine, autocommit = False, autoflush = False)
data = declarative_base()
