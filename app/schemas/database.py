from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

#  elephant database = 'postgresql://ffivcxms:OwG3mL4x_u-T9HLC3Q8Axn8mCCPTmBgP@trumpet.db.elephantsql.com/ffivcxms'
database = 'postgresql://todoapi_k4cj_user:vp2FGRZF0TJuF18xiCVs1Vx3pH7pH6Cd@dpg-cn8fna7109ks739ol93g-a/todoapi_k4cj'
engine = create_engine(database)
begin = sessionmaker(bind = engine, autocommit = False, autoflush = False)
data = declarative_base()
