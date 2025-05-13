from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

database = 'postgresql://todoapi_h5g5_user:VE8fYmbFbRnkZrMSRlWYvgdRFHHFONME@dpg-d0hkdsadbo4c73dslkag-a/todoapi_h5g5'
engine = create_engine(database)
begin = sessionmaker(bind=engine, autocommit=False, autoflush=False)
data = declarative_base()
